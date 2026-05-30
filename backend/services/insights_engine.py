from sqlalchemy.orm import Session
from services.financial_engine import FinancialEngine
from models.models import Insight
from datetime import datetime, timedelta
from typing import List
import json
import logging
import os
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class InsightsEngine:
    """Rule-based engine that generates financial insights and warnings."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.engine = FinancialEngine(db, user_id)

    def generate_insights(self) -> List[dict]:
        insights = []
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_end = month_start - timedelta(seconds=1)

        # --- Survival / Cash Flow ---
        survival = self.engine.get_survival_days()
        if survival["days"] is not None and survival["days"] < 30:
            insights.append({
                "type": "cashflow",
                "severity": survival["risk_level"],
                "message": survival["message"],
                "icon": "⚠️" if survival["risk_level"] == "warning" else "🚨"
            })

        # --- Top expense category ---
        expense_breakdown = self.engine.get_category_breakdown("expense", month_start, now)
        if expense_breakdown:
            top = expense_breakdown[0]
            if top["percentage"] > 30:
                insights.append({
                    "type": "expense_concentration",
                    "severity": "warning",
                    "message": f"'{top['category']}' accounts for {top['percentage']}% of your expenses this month. Consider reducing it.",
                    "icon": "📊"
                })

        # --- Month-over-month expense increase ---
        this_month_exp = self.engine.get_total_expenses(month_start, now)
        last_month_exp = self.engine.get_total_expenses(last_month_start, last_month_end)
        if last_month_exp > 0:
            pct_change = ((this_month_exp - last_month_exp) / last_month_exp) * 100
            if pct_change > 20:
                insights.append({
                    "type": "expense_increase",
                    "severity": "warning",
                    "message": f"Expenses increased by {round(pct_change, 1)}% compared to last month. Review your spending.",
                    "icon": "📈"
                })
            elif pct_change < -10:
                insights.append({
                    "type": "expense_decrease",
                    "severity": "info",
                    "message": f"Great job! Expenses are down {abs(round(pct_change, 1))}% compared to last month.",
                    "icon": "✅"
                })

        # --- Profit margin check ---
        monthly = self.engine.get_monthly_summary()
        if monthly["income"] > 0:
            if monthly["profit_margin"] < 0:
                insights.append({
                    "type": "loss",
                    "severity": "critical",
                    "message": f"You are running at a loss this month. Expenses exceed income by KES {abs(monthly['profit']):,.0f}.",
                    "icon": "🔴"
                })
            elif monthly["profit_margin"] < 10:
                insights.append({
                    "type": "thin_margin",
                    "severity": "warning",
                    "message": f"Your profit margin is only {monthly['profit_margin']}%. Most healthy businesses aim for 15-20%+.",
                    "icon": "⚡"
                })
            elif monthly["profit_margin"] > 30:
                insights.append({
                    "type": "strong_margin",
                    "severity": "info",
                    "message": f"Strong performance! Your profit margin is {monthly['profit_margin']}% this month.",
                    "icon": "🌟"
                })

        # --- No income this month ---
        if monthly["income"] == 0:
            insights.append({
                "type": "no_income",
                "severity": "critical",
                "message": "No income recorded this month. Are all sales being tracked?",
                "icon": "❗"
            })

        # --- Expense diversification ---
        if len(expense_breakdown) == 1 and expense_breakdown[0]["percentage"] == 100:
            insights.append({
                "type": "single_category",
                "severity": "info",
                "message": f"All expenses are in one category: '{expense_breakdown[0]['category']}'. Make sure to track all business costs.",
                "icon": "📋"
            })

        return insights

    def save_insights(self):
        """Generate and persist insights to the database."""
        raw = self.generate_insights()
        for item in raw:
            insight = Insight(
                user_id=self.user_id,
                type=item["type"],
                message=item["message"],
                severity=item["severity"],
                timestamp=datetime.utcnow()
            )
            self.db.add(insight)
        self.db.commit()
        return raw
