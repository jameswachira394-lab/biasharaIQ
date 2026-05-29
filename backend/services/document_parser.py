"""
Document parser service for BiasharaIQ.
Handles M-Pesa PDFs (password-protected), bank statements, CSVs, and invoices.
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
# Smart Category Detection
# ─────────────────────────────────────────────

# Keyword → Category mapping (M-Pesa descriptions, case-insensitive)
# Order matters: more specific rules should come first
CATEGORY_RULES = [
    # Income / Sales
    ("funds received",           "Sales"),
    ("customer payment",         "Sales"),
    ("received from",            "Sales"),
    ("payment received",         "Sales"),
    # Payroll
    ("salary",                   "Salary"),
    ("payroll",                  "Salary"),
    # Bank Transfers
    ("kcb m-pesa",               "Bank Transfer"),
    ("kcb mpesa",                "Bank Transfer"),
    ("equity",                   "Bank Transfer"),
    ("ncba",                     "Bank Transfer"),
    ("coop",                     "Bank Transfer"),
    ("cooperative bank",         "Bank Transfer"),
    ("family bank",              "Bank Transfer"),
    ("stanbic",                  "Bank Transfer"),
    ("dtb",                      "Bank Transfer"),
    ("i&m",                      "Bank Transfer"),
    ("absa",                     "Bank Transfer"),
    # Bills / Utilities
    ("pay bill",                 "Bills"),
    ("paybill",                  "Bills"),
    ("kplc",                     "Bills"),
    ("kenya power",              "Bills"),
    ("nairobi water",            "Bills"),
    ("dstv",                     "Bills"),
    ("zuku",                     "Bills"),
    ("safaricom home",           "Bills"),
    ("gotv",                     "Bills"),
    # Airtime / Data
    ("airtime",                  "Airtime"),
    ("data bundle",              "Airtime"),
    ("okoa",                     "Airtime"),
    # M-Pesa Savings / Loans
    ("m-shwari",                 "Savings"),
    ("mshwari",                  "Savings"),
    ("lock savings",             "Savings"),
    ("fuliza",                   "Loans"),
    ("kcb m-pesa loan",          "Loans"),
    # Shopping / Merchant
    ("buy goods",                "Shopping"),
    ("merchant payment",         "Shopping"),
    ("lipa na mpesa",            "Shopping"),
    ("till",                     "Shopping"),
    # Cash / Agent
    ("agent withdrawal",         "Cash Withdrawal"),
    ("agent deposit",            "Cash Deposit"),
    ("withdraw cash",            "Cash Withdrawal"),
    # Transfers
    ("transfer to",              "Transfer"),
    ("transfer from",            "Transfer"),
    ("sent to",                  "Transfer"),
    ("customer transfer",        "Transfer"),
    # Charges / Fees
    ("charge",                   "Charges"),
    ("transaction cost",         "Charges"),
    ("fee",                      "Charges"),
    # Reversals
    ("reversal",                 "Refund"),
    ("reversed",                 "Refund"),
]

def detect_category(description: str, tx_type: str = "expense") -> str:
    """
    Detect the most appropriate category for a transaction based on its description.
    Falls back to 'Income' for income-type transactions and 'Uncategorized' for expenses.
    """
    desc_lower = (description or "").lower()
    for keyword, category in CATEGORY_RULES:
        if keyword.lower() in desc_lower:
            return category
    # Sensible defaults when no rule matches
    return "Income" if tx_type == "income" else "Uncategorized"

# ─────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────

def _clean_amount(raw: str) -> Optional[Decimal]:
    try:
        cleaned = re.sub(r"[^\d.]", "", str(raw).replace(",", ""))
        return Decimal(cleaned) if cleaned else None
    except InvalidOperation:
        return None


def _parse_date(raw: str, formats: list[str]) -> Optional[datetime]:
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt)
        except ValueError:
            continue
    return None


def generate_batch_id() -> str:
    return str(uuid.uuid4())


def _open_pdf(file_bytes: bytes, password: str = ""):
    """
    Open a PDF with pdfplumber, trying the given password.
    Returns the pdfplumber PDF object (use as context manager).
    Raises PDFPasswordIncorrect if the password is wrong.
    """
    import pdfplumber
    return pdfplumber.open(io.BytesIO(file_bytes), password=password)


def _extract_pdf_text(file_bytes: bytes, password: str = "") -> str:
    """Extract all text from a PDF. Returns empty string on any error."""
    try:
        with _open_pdf(file_bytes, password) as pdf:
            return " ".join(
                (page.extract_text() or "") for page in pdf.pages
            ).lower()
    except Exception:
        return ""


# ─────────────────────────────────────────────
# M-Pesa PDF parser
# ─────────────────────────────────────────────

MPESA_DATE_FORMATS = ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M:%S"]

MPESA_ROW_RE = re.compile(
    r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\s+\d{1,2}:\d{2}(?::\d{2})?)"
    r"\s+(.+?)"
    r"\s+(Completed)"
    r"\s+([\d,]+\.\d{2}|-)"
    r"\s+([\d,]+\.\d{2}|-)"
    r"\s+([\d,]+\.\d{2})",
    re.IGNORECASE,
)

# Common M-Pesa PDF passwords: phone number formats Safaricom uses
MPESA_PASSWORD_FORMATS = [
    "{phone}",           # 0712345678
    "254{phone_local}",  # 254712345678
]


def _candidate_passwords(phone: Optional[str]) -> list[str]:
    """
    Build a list of passwords to try for an M-Pesa PDF.
    Safaricom uses the subscriber's phone number as the password.
    Tries both 07XXXXXXXX and 2547XXXXXXXX formats.
    """
    passwords = [""]  # always try no password first
    if not phone:
        return passwords
    # Normalise: strip spaces, dashes, plus
    p = re.sub(r"[\s\-\+]", "", phone)
    if p.startswith("254") and len(p) == 12:
        local = "0" + p[3:]   # 0712345678
        passwords += [p, local]
    elif p.startswith("0") and len(p) == 10:
        intl = "254" + p[1:]  # 254712345678
        passwords += [p, intl]
    else:
        passwords.append(p)
    return passwords


def parse_mpesa_pdf(file_bytes: bytes, phone: Optional[str] = None) -> list[dict]:
    """
    Parse a password-protected M-Pesa statement PDF.
    `phone` should be the subscriber's phone number (e.g. '0712345678').
    Tries multiple password formats automatically.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber is required: pip install pdfplumber")

    from pdfminer.pdfdocument import PDFPasswordIncorrect

    passwords = _candidate_passwords(phone)
    pdf_obj = None
    used_password = ""

    for pwd in passwords:
        try:
            pdf_obj = pdfplumber.open(io.BytesIO(file_bytes), password=pwd)
            used_password = pwd
            break
        except PDFPasswordIncorrect:
            continue
        except Exception as e:
            logger.error("[PARSER] Failed to open M-Pesa PDF: %s", e)
            raise

    if pdf_obj is None:
        raise ValueError(
            "This M-Pesa PDF is password-protected. "
            "Please provide your M-Pesa phone number so we can unlock it."
        )

    logger.info("[PARSER] Opened M-Pesa PDF with password format (len=%d)", len(used_password))

    transactions = []
    with pdf_obj:
        for page in pdf_obj.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 6:
                        continue
                    tx = _parse_mpesa_row(row)
                    if tx:
                        transactions.append(tx)

            if not transactions:
                text = page.extract_text() or ""
                for match in MPESA_ROW_RE.finditer(text):
                    tx = _mpesa_match_to_dict(match)
                    if tx:
                        transactions.append(tx)

    logger.info("[PARSER] M-Pesa: extracted %d transactions", len(transactions))
    return transactions


def _parse_mpesa_row(row: list) -> Optional[dict]:
    try:
        offset = 1 if len(row) >= 7 else 0
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
            "category": detect_category(details, tx_type),
            "source": "mpesa",
            "raw": details,
        }
    except Exception as e:
        logger.debug("[PARSER] Skipping M-Pesa row: %s", e)
        return None


def _mpesa_match_to_dict(match: re.Match) -> Optional[dict]:
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
        tx_type = "income" if amount > 0 else "expense"
        return {
            "date": date.isoformat(),
            "description": details,
            "amount": float(abs(amount)),
            "type": tx_type,
            "category": detect_category(details, tx_type),
            "source": "mpesa",
            "raw": details,
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
# Bank statement PDF parser
# ─────────────────────────────────────────────

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


def parse_bank_statement_pdf(file_bytes: bytes, bank_name: str = "generic", password: str = "") -> list[dict]:
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber is required: pip install pdfplumber")

    from pdfminer.pdfdocument import PDFPasswordIncorrect

    try:
        pdf_context = pdfplumber.open(io.BytesIO(file_bytes), password=password)
    except PDFPasswordIncorrect:
        raise ValueError(
            "This bank statement PDF is password-protected. "
            "Please provide the document password."
        )

    transactions = []
    with pdf_context as pdf:
        headers = None
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
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
    mapping = {}
    for i, cell in enumerate(header_row):
        if not cell:
            continue
        cell_lower = str(cell).lower().strip()
        for field, aliases in BANK_COLUMN_ALIASES.items():
            if any(alias in cell_lower for alias in aliases):
                if field not in mapping:
                    mapping[field] = i
    return mapping


def _parse_bank_row(row: list, headers: dict) -> Optional[dict]:
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
            "category": detect_category(description, tx_type),
            "source": "bank",
            "raw": description,
        }
    except Exception as e:
        logger.debug("[PARSER] Skipping bank row: %s", e)
        return None


# ─────────────────────────────────────────────
# CSV parser
# ─────────────────────────────────────────────

CSV_COLUMN_ALIASES = {**BANK_COLUMN_ALIASES}
CSV_DATE_FORMATS = BANK_DATE_FORMATS + ["%m/%d/%Y", "%Y/%m/%d"]


def parse_csv(file_bytes: bytes) -> list[dict]:
    try:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8", skip_blank_lines=True)
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1", skip_blank_lines=True)

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
            "category": detect_category(description, tx_type),
            "source": "csv",
            "raw": description,
        }
    except Exception as e:
        logger.debug("[PARSER] Skipping CSV row: %s", e)
        return None


# ─────────────────────────────────────────────
# Excel parser
# ─────────────────────────────────────────────

def parse_excel(file_bytes: bytes) -> list[dict]:
    """Parse an Excel statement (.xlsx or .xls) using pandas."""
    try:
        df = pd.read_excel(io.BytesIO(file_bytes))
        df.columns = [str(c).lower().strip() for c in df.columns]

        headers = {}
        for field, aliases in CSV_COLUMN_ALIASES.items():
            for alias in aliases:
                matches = [c for c in df.columns if alias in c]
                if matches:
                    headers[field] = matches[0]
                    break

        if "date" not in headers:
            raise ValueError("No date column detected in Excel statement")

        transactions = []
        for _, row in df.iterrows():
            tx = _parse_csv_row(row, headers)
            if tx:
                # Map source to "excel"
                tx["source"] = "excel"
                transactions.append(tx)

        logger.info("[PARSER] Excel: extracted %d transactions", len(transactions))
        return transactions

    except Exception as e:
        logger.error("[PARSER] Excel parse error: %s", e)
        raise


# ─────────────────────────────────────────────
# Invoice parser (PDF + image via Gemini)
# ─────────────────────────────────────────────

def parse_invoice(file_bytes: bytes, mime_type: str = "application/pdf") -> list[dict]:
    """
    Parse an invoice or receipt using the Veryfi Lens API.
    Requires CLIENT_ID, CLIENT_SECRET, CLIENT_API, CLIENT_USERNAME in environment.
    """
    import os
    import base64

    client_id     = os.environ.get("CLIENT_ID", "")
    client_secret = os.environ.get("CLIENT_SECRET", "")
    api_key       = os.environ.get("CLIENT_API", "")
    username      = os.environ.get("CLIENT_USERNAME", "")

    if not all([client_id, client_secret, api_key, username]):
        raise ValueError(
            "Invoice/image parsing requires Veryfi credentials. "
            "Please set CLIENT_ID, CLIENT_SECRET, CLIENT_API, and CLIENT_USERNAME "
            "in your environment, or upload a CSV/PDF bank statement instead."
        )

    try:
        from veryfi import Client as VeryfiClient
    except ImportError:
        raise RuntimeError("veryfi package is required: pip install veryfi")

    # Determine file extension for Veryfi
    ext_map = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    file_ext = ext_map.get(mime_type, ".pdf")
    file_name = f"document{file_ext}"

    try:
        veryfi_client = VeryfiClient(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            api_key=api_key,
        )
        
        import tempfile
        import os
        
        # Write bytes to a temporary file for the Veryfi SDK to process
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name
            
        try:
            response = veryfi_client.process_document(temp_file_path)
        finally:
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as cleanup_err:
                logger.warning("[PARSER] Failed to remove temp file %s: %s", temp_file_path, cleanup_err)
    except Exception as e:
        logger.error("[PARSER] Veryfi API call failed: %s", e)
        raise ValueError(f"Failed to process document with Veryfi: {e}")

    # Extract key fields from Veryfi response
    date_str  = response.get("date") or response.get("invoice_date") or ""
    vendor    = (response.get("vendor") or {}).get("name") or response.get("bill_to") or "Unknown Vendor"
    total     = response.get("total") or response.get("total_amount") or 0.0
    invoice_no = response.get("invoice_number") or ""
    description = response.get("description") or vendor

    # Parse date
    date = None
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
        try:
            date = datetime.strptime(date_str.strip(), fmt)
            break
        except (ValueError, AttributeError):
            continue
    if not date:
        date = datetime.utcnow()

    amount = _clean_amount(str(total)) or Decimal("0")

    if amount == 0:
        logger.warning("[PARSER] Veryfi returned zero amount for document")
        return []

    logger.info("[PARSER] Veryfi invoice: vendor=%s amount=%.2f", vendor, float(amount))
    return [
        {
            "date": date.isoformat(),
            "description": description,
            "amount": float(amount),
            "type": "expense",
            "source": "invoice",
            "raw": f"{vendor} | Invoice {invoice_no}",
        }
    ]


# ─────────────────────────────────────────────
# Entry point — auto-detect and dispatch
# ─────────────────────────────────────────────

def parse_document(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    phone: Optional[str] = None,
    password: str = "",
) -> tuple[list[dict], str]:
    """
    Auto-detect document type and parse it.
    - phone: subscriber phone for M-Pesa password-protected PDFs
    - password: explicit password for bank statement PDFs
    Returns (transactions, detected_type).
    """
    fname = filename.lower()

    if fname.endswith(".csv"):
        return parse_csv(file_bytes), "csv"

    if fname.endswith((".xlsx", ".xls")) or mime_type in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ):
        return parse_excel(file_bytes), "excel"

    if fname.endswith(".pdf") or mime_type == "application/pdf":
        doc_type = _detect_pdf_type(file_bytes, phone=phone, password=password)
        logger.info("[PARSER] Detected PDF type: %s", doc_type)
        if doc_type == "mpesa":
            return parse_mpesa_pdf(file_bytes, phone=phone), "mpesa"
        elif doc_type == "invoice":
            return parse_invoice(file_bytes, mime_type), "invoice"
        else:
            return parse_bank_statement_pdf(file_bytes, password=password), "bank"

    if mime_type in ("image/jpeg", "image/png", "image/webp"):
        return parse_invoice(file_bytes, mime_type), "invoice"

    raise ValueError(f"Unsupported file type: {mime_type}")


def _detect_pdf_type(
    file_bytes: bytes,
    phone: Optional[str] = None,
    password: str = "",
) -> str:
    """
    Sniff the PDF to determine its type.
    Handles password-protected M-Pesa PDFs by trying phone-derived passwords.
    Falls back to 'bank' if the type cannot be determined.
    """
    import pdfplumber
    from pdfminer.pdfdocument import PDFPasswordIncorrect

    # First try: filename hint already handled upstream, try with no password
    passwords_to_try = _candidate_passwords(phone)
    if password and password not in passwords_to_try:
        passwords_to_try.insert(0, password)

    for pwd in passwords_to_try:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes), password=pwd) as pdf:
                text = (pdf.pages[0].extract_text() or "").lower()
                if any(kw in text for kw in ["safaricom", "m-pesa", "mpesa", "fuliza"]):
                    return "mpesa"
                if any(kw in text for kw in ["invoice", "invoice no", "bill to", "amount due", "tax invoice"]):
                    return "invoice"
                return "bank"
        except PDFPasswordIncorrect:
            continue
        except Exception as e:
            logger.warning("[PARSER] _detect_pdf_type error: %s", e)
            return "bank"

    # All passwords failed — it's almost certainly a password-protected M-Pesa PDF
    # (Safaricom is the main source of password-protected statements in Kenya)
    logger.warning("[PARSER] Could not open PDF with any password — assuming mpesa")
    return "mpesa"