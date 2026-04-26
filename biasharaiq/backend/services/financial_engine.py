from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models.models import Transaction, TransactionType
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class FinancialEngine:
    """Core financial calculation engine for BiasharaIQ."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def _base_query(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        q = self.db.query(Transaction).filter(Transaction.user_id == self.user_id)
        if start_date:
            q = q.filter(Transaction.date >= start_date)
        if end_date:
            q = q.filter(Transaction.date <= end_date)
        return q

    def get_total_income(self, start_date=None, end_date=None) -> float:
        result = self._base_query(start_date, end_date).filter(
            Transaction.type == TransactionType.income
        ).with_entities(func.sum(Transaction.amount)).scalar()
        return round(result or 0.0, 2)

    def get_total_expenses(self, start_date=None, end_date=None) -> float:
        result = self._base_query(start_date, end_date).filter(
            Transaction.type == TransactionType.expense
        ).with_entities(func.sum(Transaction.amount)).scalar()
        return round(result or 0.0, 2)

    def get_profit(self, start_date=None, end_date=None) -> float:
        income = self.get_total_income(start_date, end_date)
        expenses = self.get_total_expenses(start_date, end_date)
        return round(income - expenses, 2)

    def get_balance(self) -> float:
        """Net financial position (all time)."""
        return self.get_profit()

    def get_daily_spending_rate(self, days: int = 30) -> float:
        """Average daily expense over the last N days."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        total_expenses = self.get_total_expenses(start_date, end_date)
        return round(total_expenses / days, 2) if days > 0 else 0.0

    def get_survival_days(self) -> dict:
        """How many days the business can survive at current spending rate."""
        balance = self.get_balance()
        daily_rate = self.get_daily_spending_rate()

        if daily_rate <= 0:
            return {"days": None, "risk_level": "safe", "message": "No recent spending detected."}

        if balance <= 0:
            return {"days": 0, "risk_level": "critical", "message": "Business is operating at a loss."}

        days = balance / daily_rate

        if days > 30:
            risk_level = "safe"
            message = f"Business can sustain for {int(days)} days at current spending."
        elif days > 14:
            risk_level = "warning"
            message = f"Only {int(days)} days of runway left. Review expenses soon."
        else:
            risk_level = "critical"
            message = f"CRITICAL: Only {int(days)} days of cash remaining. Act now."

        return {"days": round(days, 1), "risk_level": risk_level, "message": message}

    def get_category_breakdown(self, transaction_type: str = "expense", start_date=None, end_date=None) -> List[dict]:
        """Returns expenses/income broken down by category."""
        t_type = TransactionType.expense if transaction_type == "expense" else TransactionType.income
        rows = (
            self._base_query(start_date, end_date)
            .filter(Transaction.type == t_type)
            .with_entities(Transaction.category, func.sum(Transaction.amount).label("total"))
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )
        total = sum(r.total for r in rows) or 1
        return [
            {
                "category": r.category,
                "amount": round(r.total, 2),
                "percentage": round((r.total / total) * 100, 1)
            }
            for r in rows
        ]

    def get_weekly_trend(self, weeks: int = 8) -> List[dict]:
        """Week-by-week income vs expense trend."""
        end_date = datetime.utcnow()
        result = []
        for i in range(weeks - 1, -1, -1):
            week_end = end_date - timedelta(weeks=i)
            week_start = week_end - timedelta(weeks=1)
            income = self.get_total_income(week_start, week_end)
            expenses = self.get_total_expenses(week_start, week_end)
            result.append({
                "week": week_start.strftime("%b %d"),
                "income": income,
                "expenses": expenses,
                "profit": round(income - expenses, 2)
            })
        return result

    def get_monthly_summary(self) -> dict:
        """Current month summary."""
        now = datetime.utcnow()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        income = self.get_total_income(start, now)
        expenses = self.get_total_expenses(start, now)
        profit = round(income - expenses, 2)
        return {
            "month": now.strftime("%B %Y"),
            "income": income,
            "expenses": expenses,
            "profit": profit,
            "profit_margin": round((profit / income * 100) if income > 0 else 0, 1)
        }

    def get_full_metrics(self) -> dict:
        """Complete financial snapshot for dashboard."""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # All-time
        total_income = self.get_total_income()
        total_expenses = self.get_total_expenses()
        balance = self.get_balance()

        # This month
        month_income = self.get_total_income(month_start, now)
        month_expenses = self.get_total_expenses(month_start, now)
        month_profit = round(month_income - month_expenses, 2)

        # Cash flow
        survival = self.get_survival_days()
        daily_rate = self.get_daily_spending_rate()

        # Breakdowns
        expense_breakdown = self.get_category_breakdown("expense", month_start, now)
        income_breakdown = self.get_category_breakdown("income", month_start, now)

        return {
            "all_time": {
                "income": total_income,
                "expenses": total_expenses,
                "profit": balance,
            },
            "this_month": {
                "income": month_income,
                "expenses": month_expenses,
                "profit": month_profit,
                "profit_margin": round((month_profit / month_income * 100) if month_income > 0 else 0, 1)
            },
            "cash_flow": {
                "daily_spending_rate": daily_rate,
                "survival_days": survival["days"],
                "risk_level": survival["risk_level"],
                "message": survival["message"]
            },
            "expense_breakdown": expense_breakdown[:5],
            "income_breakdown": income_breakdown[:5],
        }
