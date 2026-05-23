"""
AI-powered transaction categorization and summarization.
Uses Claude to assign categories and generate upload summaries.
Falls back to rule-based categorization when no API key is available.
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Only instantiate clients if API keys are present
_gemini_key = os.environ.get("GEMINI_API_KEY", "")
_anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

client = None
client_type = None

if _gemini_key:
    try:
        from google import genai
        client = genai.Client(api_key=_gemini_key)
        client_type = "gemini"
        logger.info("[AI] Gemini client initialized for categorization")
    except Exception as e:
        logger.warning(f"[AI] Failed to initialize Gemini client: {e}")

if not client and _anthropic_key:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=_anthropic_key)
        client_type = "anthropic"
        logger.info("[AI] Anthropic client initialized for categorization")
    except Exception as e:
        logger.warning(f"[AI] Failed to initialize Anthropic client: {e}")

if not client:
    logger.warning("[AI] No GEMINI_API_KEY or ANTHROPIC_API_KEY set — using rule-based categorization fallback")


# ─────────────────────────────────────────────
# Category mapping prompt
# ─────────────────────────────────────────────

CATEGORIZE_SYSTEM = """You are a financial assistant for Kenyan SMEs using BiasharaIQ.
Your job is to assign a category to each transaction based on its description.

Available expense categories:
Rent, Utilities, Salaries, Stock/Inventory, Transport, Airtime/Internet,
Marketing, Equipment, Bank Charges, Taxes, Food & Supplies, Repairs & Maintenance, Other Expense

Available income categories:
Sales, Services Rendered, M-Pesa Collections, Bank Transfer In, Refund, Other Income

Rules:
- M-Pesa send money / till / paybill → use context clues for category
- "KPLC" or "Kenya Power" → Utilities
- "Safaricom" airtime/data → Airtime/Internet
- "salary" or "wages" → Salaries (expense) or ignore if income
- "rent" → Rent
- Transfers between own accounts → Bank Charges or ignore
- When unsure → Other Expense or Other Income

Return ONLY a JSON array, no markdown, no explanation:
[{"index": 0, "category": "category name", "confidence": 0.95}, ...]"""


def categorize_transactions(transactions: list[dict], user_categories: list[str] = None) -> list[dict]:
    """
    Use Claude to assign a category to each transaction.
    Returns transactions with 'suggested_category' field added.
    """
    if not transactions:
        return transactions

    # Build a compact representation for the prompt
    items = [
        {"index": i, "description": tx["description"], "amount": tx["amount"], "type": tx["type"]}
        for i, tx in enumerate(transactions)
    ]

    # Process in batches of 50 to stay within token limits
    batch_size = 50
    all_results = {}

    for start in range(0, len(items), batch_size):
        batch = items[start : start + batch_size]
        batch_results = _categorize_batch(batch, user_categories)
        all_results.update(batch_results)

    # Merge categories back into transactions
    enriched = []
    for i, tx in enumerate(transactions):
        result = all_results.get(i, {})
        enriched.append({
            **tx,
            "suggested_category": result.get("category", "Other Expense" if tx["type"] == "expense" else "Other Income"),
            "category_confidence": result.get("confidence", 0.5),
        })

    return enriched


# ─────────────────────────────────────────────
# Rule-based fallback categorizer
# ─────────────────────────────────────────────

RULE_KEYWORDS = {
    "expense": {
        "Rent": ["rent", "rental", "lease"],
        "Utilities": ["kplc", "kenya power", "water", "nawasco", "nairobi water", "electricity", "utility"],
        "Airtime/Internet": ["safaricom", "airtel", "telkom", "airtime", "data", "internet", "wifi"],
        "Salaries": ["salary", "salaries", "wages", "payroll", "staff"],
        "Transport": ["fuel", "transport", "uber", "bolt", "matatu", "taxi", "petrol", "diesel"],
        "Stock/Inventory": ["stock", "inventory", "goods", "merchandise", "supplier", "purchase"],
        "Bank Charges": ["bank charge", "transaction fee", "service charge", "ledger fee", "excise"],
        "Marketing": ["advert", "marketing", "promotion", "google", "facebook", "meta ads"],
        "Food & Supplies": ["food", "grocery", "supermarket", "naivas", "quickmart", "carrefour", "cleanshelf"],
        "Equipment": ["equipment", "machine", "laptop", "phone", "computer", "printer"],
    },
    "income": {
        "M-Pesa Collections": ["mpesa", "m-pesa", "paybill", "till", "lipa na"],
        "Sales": ["sale", "payment received", "invoice paid", "customer"],
        "Bank Transfer In": ["transfer in", "bank transfer", "eft", "rtgs", "swift"],
        "Refund": ["refund", "reversal", "chargeback", "returned"],
    },
}

def _rule_based_category(description: str, tx_type: str) -> str:
    """Simple keyword-based fallback categorization."""
    desc_lower = description.lower()
    rules = RULE_KEYWORDS.get(tx_type, {})
    for category, keywords in rules.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "Other Expense" if tx_type == "expense" else "Other Income"


def _categorize_batch(items: list[dict], user_categories: list[str] = None) -> dict:
    """Categorize a batch of transactions. Returns {index: {category, confidence}}.
    Uses Gemini or Claude when available, falls back to rule-based when no API key.
    """
    # Fall back to rule-based if no AI client
    if client is None:
        logger.info("[AI] Using rule-based categorization (no AI key)")
        return {
            item["index"]: {
                "category": _rule_based_category(item["description"], item["type"]),
                "confidence": 0.6,
            }
            for item in items
        }

    system = CATEGORIZE_SYSTEM
    if user_categories:
        system += f"\n\nThis user's custom categories: {', '.join(user_categories)}"

    prompt = f"Categorize these transactions:\n{json.dumps(items, indent=2)}"

    try:
        if client_type == "gemini":
            from google.genai import types
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    temperature=0.1,
                )
            )
            raw = response.text.strip()
        else:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()

        # Strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        results = json.loads(raw)

        return {r["index"]: {"category": r["category"], "confidence": r.get("confidence", 0.8)}
                for r in results}

    except Exception as e:
        logger.error("[AI] Categorization batch failed: %s — falling back to rules", e)
        return {
            item["index"]: {
                "category": _rule_based_category(item["description"], item["type"]),
                "confidence": 0.5,
            }
            for item in items
        }



# ─────────────────────────────────────────────
# Upload summary generation
# ─────────────────────────────────────────────

def generate_upload_summary(transactions: list[dict], doc_type: str) -> dict:
    """
    Generate a human-readable summary of an uploaded document.
    Returns a summary dict with totals and AI narrative.
    """
    if not transactions:
        return {
            "transaction_count": 0,
            "total_income": 0,
            "total_expenses": 0,
            "net": 0,
            "narrative": "No transactions were found in this document.",
            "top_categories": [],
        }

    income_txs = [t for t in transactions if t["type"] == "income"]
    expense_txs = [t for t in transactions if t["type"] == "expense"]

    total_income = sum(t["amount"] for t in income_txs)
    total_expenses = sum(t["amount"] for t in expense_txs)
    net = total_income - total_expenses

    # Aggregate by suggested_category
    category_totals: dict[str, float] = {}
    for tx in transactions:
        cat = tx.get("suggested_category", "Uncategorized")
        category_totals[cat] = category_totals.get(cat, 0) + tx["amount"]

    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    # Generate narrative
    narrative = _generate_narrative(
        doc_type=doc_type,
        count=len(transactions),
        total_income=total_income,
        total_expenses=total_expenses,
        net=net,
        top_categories=top_categories,
    )

    return {
        "transaction_count": len(transactions),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net": round(net, 2),
        "narrative": narrative,
        "top_categories": [{"category": c, "amount": round(a, 2)} for c, a in top_categories],
    }


def _generate_narrative(
    doc_type: str,
    count: int,
    total_income: float,
    total_expenses: float,
    net: float,
    top_categories: list,
) -> str:
    """Ask AI for a concise 2-3 sentence financial summary.
    Falls back to a template string when no AI client is available.
    """
    direction = "surplus" if net >= 0 else "deficit"
    fallback = (
        f"Imported {count} transactions from your {doc_type} statement. "
        f"Total income: KES {total_income:,.2f}, total expenses: KES {total_expenses:,.2f}. "
        f"Net {direction}: KES {abs(net):,.2f}."
    )

    if client is None:
        return fallback

    try:
        cat_str = ", ".join(f"{c} (KES {a:,.0f})" for c, a in top_categories[:3])
        prompt = (
            f"Summarize this {doc_type} upload for a Kenyan SME owner in 2-3 sentences. "
            f"Be specific with numbers. Use KES for currency.\n\n"
            f"Transactions: {count}\n"
            f"Total Income: KES {total_income:,.2f}\n"
            f"Total Expenses: KES {total_expenses:,.2f}\n"
            f"Net: KES {net:,.2f}\n"
            f"Top spending areas: {cat_str}"
        )

        if client_type == "gemini":
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt],
            )
            return response.text.strip()
        else:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()

    except Exception as e:
        logger.error("[AI] Narrative generation failed: %s", e)
        return fallback

