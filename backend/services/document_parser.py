"""
Document parser service for BiasharaIQ.
Handles M-Pesa PDFs, bank statements, CSVs, and invoices.
"""

import re
import io
import uuid
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────

def _clean_amount(raw: str) -> Optional[Decimal]:
    """Strip commas, currency symbols, and whitespace then parse as Decimal."""
    try:
        cleaned = re.sub(r"[^\d.]", "", str(raw).replace(",", ""))
        return Decimal(cleaned) if cleaned else None
    except InvalidOperation:
        return None


def _parse_date(raw: str, formats: list[str]) -> Optional[datetime]:
    """Try multiple date formats and return the first that parses."""
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt)
        except ValueError:
            continue
    return None


def generate_batch_id() -> str:
    return str(uuid.uuid4())


# ─────────────────────────────────────────────
# M-Pesa PDF parser
# ─────────────────────────────────────────────

MPESA_DATE_FORMATS = ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M:%S"]

# Regex for M-Pesa statement rows:
# Completion Time | Details | Transaction Status | Paid In | Withdrawn | Balance
MPESA_ROW_RE = re.compile(
    r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\s+\d{1,2}:\d{2}(?::\d{2})?)"  # date/time
    r"\s+(.+?)"                                                           # details
    r"\s+(Completed)"                                                     # status
    r"\s+([\d,]+\.\d{2}|-)"                                              # paid in
    r"\s+([\d,]+\.\d{2}|-)"                                              # withdrawn
    r"\s+([\d,]+\.\d{2})",                                               # balance
    re.IGNORECASE,
)


def parse_mpesa_pdf(file_bytes: bytes) -> list[dict]:
    """
    Parse an M-Pesa statement PDF and return a list of transaction dicts.
    Handles the standard Safaricom statement format.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber is required: pip install pdfplumber")

    transactions = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # Try table extraction first (more reliable)
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 6:
                        continue
                    tx = _parse_mpesa_row(row)
                    if tx:
                        transactions.append(tx)

            # Fallback: regex on raw text
            if not transactions:
                text = page.extract_text() or ""
                for match in MPESA_ROW_RE.finditer(text):
                    tx = _mpesa_match_to_dict(match)
                    if tx:
                        transactions.append(tx)

    logger.info("[PARSER] M-Pesa: extracted %d transactions", len(transactions))
    return transactions


def _parse_mpesa_row(row: list) -> Optional[dict]:
    """Parse a table row from an M-Pesa PDF."""
    try:
        # Columns: Receipt No | Completion Time | Details | Status | Paid In | Withdrawn | Balance
        # Some statements omit receipt no — handle both
        offset = 0
        if len(row) >= 7:
            offset = 1  # receipt number present

        date_str = str(row[offset] or "").strip()
        details = str(row[offset + 1] or "").strip()
        status = str(row[offset + 2] or "").strip()
        paid_in_raw = str(row[offset + 3] or "-").strip()
        withdrawn_raw = str(row[offset + 4] or "-").strip()

        if "completed" not in status.lower():
            return None

        date = _parse_date(date_str, MPESA_DATE_FORMATS)
        if not date:
            return None

        paid_in = _clean_amount(paid_in_raw) if paid_in_raw != "-" else Decimal("0")
        withdrawn = _clean_amount(withdrawn_raw) if withdrawn_raw != "-" else Decimal("0")

        if not paid_in and not withdrawn:
            return None

        amount = paid_in if paid_in > 0 else -withdrawn
        tx_type = "income" if amount > 0 else "expense"

        return {
            "date": date.isoformat(),
            "description": details,
            "amount": float(abs(amount)),
            "type": tx_type,
            "source": "mpesa",
            "raw": details,
        }
    except Exception as e:
        logger.debug("[PARSER] Skipping M-Pesa row: %s", e)
        return None


def _mpesa_match_to_dict(match: re.Match) -> Optional[dict]:
    """Convert a regex match to a transaction dict."""
    try:
        date = _parse_date(match.group(1), MPESA_DATE_FORMATS)
        if not date:
            return None
        details = match.group(2).strip()
        paid_in_raw = match.group(4)
        withdrawn_raw = match.group(5)

        paid_in = _clean_amount(paid_in_raw) if paid_in_raw != "-" else Decimal("0")
        withdrawn = _clean_amount(withdrawn_raw) if withdrawn_raw != "-" else Decimal("0")

        amount = paid_in if paid_in > 0 else -withdrawn
        return {
            "date": date.isoformat(),
            "description": details,
            "amount": float(abs(amount)),
            "type": "income" if amount > 0 else "expense",
            "source": "mpesa",
            "raw": details,
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
# Bank statement PDF parser
# ─────────────────────────────────────────────

# Known Kenyan bank column patterns
BANK_COLUMN_ALIASES = {
    "date": ["date", "value date", "trans date", "transaction date", "posting date"],
    "description": ["description", "details", "narration", "particulars", "remarks", "reference"],
    "debit": ["debit", "dr", "withdrawals", "withdrawn", "debit amount"],
    "credit": ["credit", "cr", "deposits", "paid in", "credit amount"],
    "balance": ["balance", "running balance", "closing balance"],
}

BANK_DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d-%b-%Y",
    "%d/%m/%y", "%Y-%m-%d", "%d %B %Y",
]


def parse_bank_statement_pdf(file_bytes: bytes, bank_name: str = "generic") -> list[dict]:
    """
    Parse a bank statement PDF.
    Supports KCB, Equity, Co-op, and generic formats.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber is required: pip install pdfplumber")

    transactions = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        headers = None
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                # Detect header row
                if headers is None:
                    headers = _detect_bank_headers(table[0])
                    start_row = 1
                else:
                    start_row = 0

                for row in table[start_row:]:
                    tx = _parse_bank_row(row, headers)
                    if tx:
                        transactions.append(tx)

    logger.info("[PARSER] Bank (%s): extracted %d transactions", bank_name, len(transactions))
    return transactions


def _detect_bank_headers(header_row: list) -> dict:
    """Map column indices to standard field names."""
    mapping = {}
    for i, cell in enumerate(header_row):
        if not cell:
            continue
        cell_lower = str(cell).lower().strip()
        for field, aliases in BANK_COLUMN_ALIASES.items():
            if any(alias in cell_lower for alias in aliases):
                if field not in mapping:  # first match wins
                    mapping[field] = i
    return mapping


def _parse_bank_row(row: list, headers: dict) -> Optional[dict]:
    """Parse a single bank statement row using detected headers."""
    try:
        if not headers or "date" not in headers:
            return None

        date_raw = str(row[headers["date"]] or "").strip()
        date = _parse_date(date_raw, BANK_DATE_FORMATS)
        if not date:
            return None

        description = ""
        if "description" in headers:
            description = str(row[headers["description"]] or "").strip()

        debit = Decimal("0")
        credit = Decimal("0")

        if "debit" in headers:
            raw = str(row[headers["debit"]] or "").strip()
            debit = _clean_amount(raw) or Decimal("0")

        if "credit" in headers:
            raw = str(row[headers["credit"]] or "").strip()
            credit = _clean_amount(raw) or Decimal("0")

        if debit == 0 and credit == 0:
            return None

        amount = credit if credit > 0 else debit
        tx_type = "income" if credit > 0 else "expense"

        return {
            "date": date.isoformat(),
            "description": description,
            "amount": float(amount),
            "type": tx_type,
            "source": "bank",
            "raw": description,
        }
    except Exception as e:
        logger.debug("[PARSER] Skipping bank row: %s", e)
        return None


# ─────────────────────────────────────────────
# CSV parser
# ─────────────────────────────────────────────

CSV_COLUMN_ALIASES = {**BANK_COLUMN_ALIASES}  # reuse same aliases

CSV_DATE_FORMATS = BANK_DATE_FORMATS + ["%m/%d/%Y", "%Y/%m/%d"]


def parse_csv(file_bytes: bytes) -> list[dict]:
    """
    Parse a CSV transaction export.
    Auto-detects column layout using common aliases.
    """
    try:
        # Try UTF-8 first, fall back to latin-1 (common in Kenyan bank exports)
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8", skip_blank_lines=True)
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1", skip_blank_lines=True)

        # Normalise column names
        df.columns = [str(c).lower().strip() for c in df.columns]

        headers = {}
        for field, aliases in CSV_COLUMN_ALIASES.items():
            for alias in aliases:
                matches = [c for c in df.columns if alias in c]
                if matches:
                    headers[field] = matches[0]
                    break

        if "date" not in headers:
            raise ValueError("No date column detected in CSV")

        transactions = []
        for _, row in df.iterrows():
            tx = _parse_csv_row(row, headers)
            if tx:
                transactions.append(tx)

        logger.info("[PARSER] CSV: extracted %d transactions", len(transactions))
        return transactions

    except Exception as e:
        logger.error("[PARSER] CSV parse error: %s", e)
        raise


def _parse_csv_row(row: pd.Series, headers: dict) -> Optional[dict]:
    """Parse a single CSV row."""
    try:
        date_raw = str(row.get(headers["date"], "")).strip()
        date = _parse_date(date_raw, CSV_DATE_FORMATS)
        if not date:
            return None

        description = str(row.get(headers.get("description", ""), "")).strip()

        debit = Decimal("0")
        credit = Decimal("0")

        if "debit" in headers:
            debit = _clean_amount(str(row.get(headers["debit"], "0"))) or Decimal("0")
        if "credit" in headers:
            credit = _clean_amount(str(row.get(headers["credit"], "0"))) or Decimal("0")

        # Some CSVs use a single "amount" column with +/- signs
        if debit == 0 and credit == 0 and "amount" in row.index:
            raw = str(row["amount"]).strip()
            val = _clean_amount(raw)
            if val is not None:
                signed_raw = re.sub(r"[^\d.\-]", "", raw)
                is_negative = signed_raw.startswith("-")
                credit = val if not is_negative else Decimal("0")
                debit = val if is_negative else Decimal("0")

        if debit == 0 and credit == 0:
            return None

        amount = credit if credit > 0 else debit
        tx_type = "income" if credit > 0 else "expense"

        return {
            "date": date.isoformat(),
            "description": description,
            "amount": float(amount),
            "type": tx_type,
            "source": "csv",
            "raw": description,
        }
    except Exception as e:
        logger.debug("[PARSER] Skipping CSV row: %s", e)
        return None


# ─────────────────────────────────────────────
# Invoice parser (PDF + image via Claude API)
# ─────────────────────────────────────────────

def parse_invoice(file_bytes: bytes, mime_type: str = "application/pdf") -> list[dict]:
    """
    Parse an invoice using Claude's vision API.
    Returns a list with a single transaction (the invoice total).
    """
    import anthropic
    import base64

    client = anthropic.Anthropic()
    b64 = base64.standard_b64encode(file_bytes).decode("utf-8")

    prompt = """Extract the following from this invoice and return ONLY valid JSON, no markdown:
{
  "date": "YYYY-MM-DD or null",
  "vendor": "vendor/supplier name",
  "description": "brief description of goods/services",
  "amount": 0.00,
  "currency": "KES",
  "invoice_number": "invoice number or null"
}
If you cannot determine a field, use null. Amount should be the total payable amount as a number."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document" if "pdf" in mime_type else "image",
                        "source": {"type": "base64", "media_type": mime_type, "data": b64},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    import json
    raw_text = response.content[0].text.strip()
    data = json.loads(raw_text)

    date_str = data.get("date")
    date = _parse_date(date_str, ["%Y-%m-%d"]) if date_str else datetime.utcnow()

    amount = _clean_amount(str(data.get("amount", 0))) or Decimal("0")
    description = data.get("description") or data.get("vendor") or "Invoice"

    if amount == 0:
        return []

    logger.info("[PARSER] Invoice: extracted 1 transaction (amount=%.2f)", float(amount))
    return [
        {
            "date": (date or datetime.utcnow()).isoformat(),
            "description": description,
            "amount": float(amount),
            "type": "expense",
            "source": "invoice",
            "raw": f"{data.get('vendor','')} | Invoice {data.get('invoice_number','')}",
        }
    ]


# ─────────────────────────────────────────────
# Entry point — auto-detect and dispatch
# ─────────────────────────────────────────────

def parse_document(file_bytes: bytes, filename: str, mime_type: str) -> tuple[list[dict], str]:
    """
    Auto-detect document type and parse it.
    Returns (transactions, detected_type).
    """
    fname = filename.lower()

    if fname.endswith(".csv"):
        return parse_csv(file_bytes), "csv"

    if fname.endswith(".pdf") or mime_type == "application/pdf":
        # Sniff the PDF text to distinguish M-Pesa vs bank vs invoice
        doc_type = _detect_pdf_type(file_bytes)
        if doc_type == "mpesa":
            return parse_mpesa_pdf(file_bytes), "mpesa"
        elif doc_type == "invoice":
            return parse_invoice(file_bytes, mime_type), "invoice"
        else:
            return parse_bank_statement_pdf(file_bytes), "bank"

    if mime_type in ("image/jpeg", "image/png", "image/webp"):
        return parse_invoice(file_bytes, mime_type), "invoice"

    raise ValueError(f"Unsupported file type: {mime_type}")


def _detect_pdf_type(file_bytes: bytes) -> str:
    """Sniff the first page of a PDF to determine its type."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = (pdf.pages[0].extract_text() or "").lower()
            if any(kw in text for kw in ["safaricom", "m-pesa", "mpesa", "fuliza"]):
                return "mpesa"
            if any(kw in text for kw in ["invoice", "invoice no", "bill to", "amount due", "tax invoice"]):
                return "invoice"
            return "bank"
    except Exception:
        return "bank"
