"""
Intent classifier for user financial questions.

Routes questions to appropriate financial engines based on user intent.
"""

import re
from enum import Enum
from typing import Optional


class Intent(Enum):
    """Supported financial question intents."""
    PROFITABILITY = "profitability"  # Why losing/making money?
    CASHFLOW = "cashflow"  # How long can we survive?
    EXPENSES = "expenses"  # Which expenses to cut?
    RISK = "risk"  # What are the risks?
    TRENDS = "trends"  # How are we trending?
    GENERAL = "general"  # General question


# Map keywords to intents
INTENT_KEYWORDS = {
    Intent.PROFITABILITY: [
        r"why.*los(ing|e|t)",
        r"losing.*money",
        r"unprofitable",
        r"profit\s*(margin)?",
        r"why.*not.*making",
        r"making.*money",
        r"why.*so.*low",
        r"revenue.*low",
        r"expensive",
    ],
    Intent.CASHFLOW: [
        r"survive",
        r"how.*long",
        r"runway",
        r"cash.*left",
        r"days.*left",
        r"burn.*rate",
        r"sustain",
        r"running.*out",
    ],
    Intent.EXPENSES: [
        r"cut.*spending",
        r"cut.*cost",
        r"reduce.*spending",
        r"reduce.*expense",
        r"reduce.*cost",
        r"where.*cut",
        r"expensive\s*category",
        r"expensive\s*line",
        r"high.*cost",
        r"expensive.*item",
        r"costs.*should",
        r"expense.*cut",
    ],
    Intent.RISK: [
        r"risk",
        r"problem",
        r"concern",
        r"challenge",
        r"warning",
        r"danger",
        r"worry",
    ],
    Intent.TRENDS: [
        r"trend",
        r"growing",
        r"shrinking",
        r"improving",
        r"getting.*worse",
        r"up\s*\d",
        r"down\s*\d",
        r"month.*month",
    ],
}


def classify_intent(user_message: str) -> Intent:
    """
    Classify a user message into a financial intent.

    Returns the matched intent, or GENERAL if no strong match.
    """
    message_lower = user_message.lower().strip()

    # Try to match against intent keywords
    for intent, patterns in INTENT_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return intent

    # Default to general Q&A
    return Intent.GENERAL


def get_intent_description(intent: Intent) -> str:
    """Get human-readable description of an intent."""
    descriptions = {
        Intent.PROFITABILITY: "Profitability Analysis",
        Intent.CASHFLOW: "Cash Flow Survival",
        Intent.EXPENSES: "Expense Optimization",
        Intent.RISK: "Risk Detection",
        Intent.TRENDS: "Trend Analysis",
        Intent.GENERAL: "General Financial Q&A",
    }
    return descriptions.get(intent, "Unknown")
