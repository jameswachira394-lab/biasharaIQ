"""
Context builder for intent-based AI prompts.

Generates minimal, focused context for each financial question type.
Replaces the old approach of sending all data to the AI.
"""

from sqlalchemy.orm import Session
from services.intent_classifier import Intent
from services.analysis_engines import (
    ProfitabilityEngine,
    CashflowEngine,
    ExpenseOptimizerEngine,
    RiskDetectorEngine,
)
from typing import Dict, Tuple


class ContextBuilder:
    """Builds minimal, focused AI context based on user intent."""

    def __init__(self, db: Session, user_id: int, business_name: str):
        self.db = db
        self.user_id = user_id
        self.business_name = business_name

    def build_for_intent(self, intent: Intent, user_message: str) -> Dict:
        """
        Build focused context for the given intent.

        Returns dict with:
        - "context_text": compact string for AI
        - "analysis": structured analysis data
        - "max_tokens": suggested token limit
        """
        if intent == Intent.PROFITABILITY:
            return self._build_profitability_context()
        elif intent == Intent.CASHFLOW:
            return self._build_cashflow_context()
        elif intent == Intent.EXPENSES:
            return self._build_expense_context()
        elif intent == Intent.RISK:
            return self._build_risk_context()
        elif intent == Intent.TRENDS:
            return self._build_trends_context()
        else:
            return self._build_general_context()

    def _build_profitability_context(self) -> Dict:
        """Context for profitability questions: Why am I losing money?"""
        engine = ProfitabilityEngine(self.db, self.user_id)
        analysis = engine.analyze()

        context_text = f"""
Business: {self.business_name}

PROFITABILITY THIS MONTH:
- Revenue: KES {analysis['revenue']:,.0f}
- Expenses: KES {analysis['expenses']:,.0f}
- Profit: KES {analysis['profit']:,.0f}
- Margin: {analysis['profit_margin']:.1f}%

TRENDS (vs last month):
- Revenue: {analysis['revenue_trend']}
- Expenses: {analysis['expense_trend']}

TOP EXPENSES:
{self._format_expense_list(analysis['top_expenses'])}

CONTEXT: Is the business profitable this month? What's driving the profit or loss?
""".strip()

        return {
            "context_text": context_text,
            "analysis": analysis,
            "max_tokens": 300,
        }

    def _build_cashflow_context(self) -> Dict:
        """Context for cashflow questions: How long can we survive?"""
        engine = CashflowEngine(self.db, self.user_id)
        analysis = engine.analyze()

        context_text = f"""
Business: {self.business_name}

CASH POSITION:
- Current balance: KES {analysis['balance']:,.0f}
- Daily spending: KES {analysis['daily_burn']:,.0f}
- Days of runway: {analysis['survival_days'] or 'N/A'}

RISK LEVEL: {analysis['risk_level'].upper()}

CONTEXT: How many days can this business operate at current spending rate?
""".strip()

        return {
            "context_text": context_text,
            "analysis": analysis,
            "max_tokens": 250,
        }

    def _build_expense_context(self) -> Dict:
        """Context for expense questions: Which expenses should we cut?"""
        engine = ExpenseOptimizerEngine(self.db, self.user_id)
        analysis = engine.analyze()

        context_text = f"""
Business: {self.business_name}

TOTAL EXPENSES THIS MONTH: KES {analysis['total_expenses']:,.0f}

TOP EXPENSE CATEGORIES (by impact):
{self._format_optimization_list(analysis['top_categories'])}

KEY INSIGHTS:
- Fastest growing: {analysis['highest_growth']}
- Largest category: {analysis['highest_amount']}

CONTEXT: Which expense categories offer the best opportunity for cost reduction?
""".strip()

        return {
            "context_text": context_text,
            "analysis": analysis,
            "max_tokens": 300,
        }

    def _build_risk_context(self) -> Dict:
        """Context for risk questions: What are my financial risks?"""
        engine = RiskDetectorEngine(self.db, self.user_id)
        analysis = engine.analyze()

        risk_summary = "\n".join(
            f"- {risk['message']} [{risk['severity'].upper()}]"
            for risk in analysis['risks']
        )

        context_text = f"""
Business: {self.business_name}

IDENTIFIED FINANCIAL RISKS:
{risk_summary}

TOTAL RISKS: {analysis['risk_count']}

CONTEXT: What are the main financial risks? Which need immediate attention?
""".strip()

        return {
            "context_text": context_text,
            "analysis": analysis,
            "max_tokens": 350,
        }

    def _build_trends_context(self) -> Dict:
        """Context for trend questions: How are we trending?"""
        engine = ProfitabilityEngine(self.db, self.user_id)
        analysis = engine.analyze()

        context_text = f"""
Business: {self.business_name}

MONTH-OVER-MONTH COMPARISON:

This Month:
- Revenue: KES {analysis['revenue']:,.0f} ({analysis['revenue_trend']})
- Expenses: KES {analysis['expenses']:,.0f} ({analysis['expense_trend']})
- Profit: KES {analysis['profit']:,.0f}
- Margin: {analysis['profit_margin']:.1f}%

Last Month:
- Profit: KES {analysis['previous_month']['profit']:,.0f}
- Margin: {analysis['previous_month']['margin']:.1f}%

CONTEXT: Are trends improving or declining? What's driving the changes?
""".strip()

        return {
            "context_text": context_text,
            "analysis": analysis,
            "max_tokens": 300,
        }

    def _build_general_context(self) -> Dict:
        """Fallback context for general questions."""
        profit_engine = ProfitabilityEngine(self.db, self.user_id)
        profit_analysis = profit_engine.analyze()

        cashflow_engine = CashflowEngine(self.db, self.user_id)
        cashflow_analysis = cashflow_engine.analyze()

        context_text = f"""
Business: {self.business_name}

QUICK SUMMARY:
- This month revenue: KES {profit_analysis['revenue']:,.0f}
- This month expenses: KES {profit_analysis['expenses']:,.0f}
- This month profit: KES {profit_analysis['profit']:,.0f}
- Cash runway: {cashflow_analysis['survival_days'] or 'N/A'} days
- Status: {'Profitable' if profit_analysis['is_profitable'] else 'Operating at loss'}

CONTEXT: Provide helpful financial insights for the business. Be specific, data-driven, and concise.
""".strip()

        return {
            "context_text": context_text,
            "analysis": {
                "profitability": profit_analysis,
                "cashflow": cashflow_analysis,
            },
            "max_tokens": 350,
        }

    @staticmethod
    def _format_expense_list(expenses: list) -> str:
        """Format expense list for display."""
        if not expenses:
            return "No expense data available."

        lines = []
        for exp in expenses:
            lines.append(
                f"  • {exp['category']}: KES {exp['amount']:,.0f} ({exp['percentage']:.1f}%)"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_optimization_list(categories: list) -> str:
        """Format category optimization data."""
        if not categories:
            return "No expense data available."

        lines = []
        for cat in categories[:5]:
            growth_str = f"(↑{cat['growth']:.0f}%)" if cat["growth"] > 0 else f"(↓{abs(cat['growth']):.0f}%)"
            lines.append(
                f"  • {cat['category']}: KES {cat['amount']:,.0f} {growth_str}"
            )
        return "\n".join(lines)
