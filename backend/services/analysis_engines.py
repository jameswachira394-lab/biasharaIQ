"""
Specialized financial analysis engines for BiasharaIQ.

Each engine focuses on a specific financial question type and generates
compact, structured insights that the AI can explain naturally.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from models.models import Transaction, TransactionType
from typing import Dict, List, Optional


class ProfitabilityEngine:
    """Analyzes profit margins, losses, and revenue/expense trends."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def analyze(self) -> Dict:
        """
        Generate compact profitability analysis.

        Returns structured data suitable for AI explanation.
        """
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_end = month_start - timedelta(seconds=1)

        # Current month metrics
        current_revenue = self._get_revenue(month_start, now)
        current_expenses = self._get_expenses(month_start, now)
        current_profit = current_revenue - current_expenses
        current_margin = (current_profit / current_revenue * 100) if current_revenue > 0 else 0

        # Last month metrics
        last_revenue = self._get_revenue(last_month_start, last_month_end)
        last_expenses = self._get_expenses(last_month_start, last_month_end)
        last_profit = last_revenue - last_expenses
        last_margin = (last_profit / last_revenue * 100) if last_revenue > 0 else 0

        # Calculate trends
        revenue_trend = self._calculate_trend(last_revenue, current_revenue)
        expense_trend = self._calculate_trend(last_expenses, current_expenses)

        # Top expense categories
        top_expenses = self._get_top_expenses(month_start, now, limit=3)

        return {
            "period": "this month",
            "revenue": round(current_revenue, 2),
            "expenses": round(current_expenses, 2),
            "profit": round(current_profit, 2),
            "profit_margin": round(current_margin, 1),
            "is_profitable": current_profit >= 0,
            "revenue_trend": revenue_trend,
            "expense_trend": expense_trend,
            "top_expenses": top_expenses,
            "previous_month": {
                "profit": round(last_profit, 2),
                "margin": round(last_margin, 1),
            }
        }

    def _get_revenue(self, start: datetime, end: datetime) -> float:
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.income,
                Transaction.date >= start,
                Transaction.date <= end,
            )
            .scalar()
        )
        return float(result or 0)

    def _get_expenses(self, start: datetime, end: datetime) -> float:
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= start,
                Transaction.date <= end,
            )
            .scalar()
        )
        return float(result or 0)

    def _calculate_trend(self, previous: float, current: float) -> str:
        """Calculate percentage change and return trend description."""
        if previous == 0:
            return "new activity" if current > 0 else "stable"

        pct_change = ((current - previous) / previous) * 100

        if abs(pct_change) < 5:
            return "stable"
        elif pct_change > 0:
            return f"up {abs(round(pct_change, 0))}%"
        else:
            return f"down {abs(round(pct_change, 0))}%"

    def _get_top_expenses(self, start: datetime, end: datetime, limit: int = 3) -> List[Dict]:
        """Get top expense categories."""
        rows = (
            self.db.query(Transaction.category, func.sum(Transaction.amount).label("total"))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= start,
                Transaction.date <= end,
            )
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(limit)
            .all()
        )

        total_expenses = self._get_expenses(start, end)

        return [
            {
                "category": row.category,
                "amount": round(row.total, 2),
                "percentage": round((row.total / total_expenses * 100), 1) if total_expenses > 0 else 0,
            }
            for row in rows
        ]


class CashflowEngine:
    """Calculates cash runway and survival metrics."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def analyze(self) -> Dict:
        """
        Calculate cash survival metrics.

        Returns: days of runway, risk level, and recommendations.
        """
        balance = self._get_balance()
        daily_burn = self._get_daily_burn_rate(days=30)

        if daily_burn <= 0:
            return {
                "balance": round(balance, 2),
                "daily_burn": 0,
                "survival_days": None,
                "risk_level": "safe",
                "message": "No recent spending detected or positive cash generation.",
            }

        if balance <= 0:
            return {
                "balance": round(balance, 2),
                "daily_burn": round(daily_burn, 2),
                "survival_days": 0,
                "risk_level": "critical",
                "message": "Business has zero or negative balance. Critical situation.",
            }

        survival_days = balance / daily_burn

        if survival_days > 90:
            risk_level = "safe"
        elif survival_days > 30:
            risk_level = "warning"
        else:
            risk_level = "critical"

        return {
            "balance": round(balance, 2),
            "daily_burn": round(daily_burn, 2),
            "survival_days": round(survival_days, 1),
            "risk_level": risk_level,
        }

    def _get_balance(self) -> float:
        """Get all-time net balance (all income - all expenses)."""
        income = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.income,
            )
            .scalar()
        )
        expenses = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
            )
            .scalar()
        )
        return float(income or 0) - float(expenses or 0)

    def _get_daily_burn_rate(self, days: int = 30) -> float:
        """Average daily spending over last N days."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        total_expenses = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )
        return float(total_expenses or 0) / days if days > 0 else 0.0


class ExpenseOptimizerEngine:
    """Identifies which expenses to cut and optimization opportunities."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def analyze(self) -> Dict:
        """
        Identify optimization opportunities.

        Returns: recommendations ranked by impact.
        """
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_end = month_start - timedelta(seconds=1)

        # Get categories with growth rates
        categories = self._get_expense_categories(month_start, now)
        growth_rates = self._calculate_growth_rates(categories, last_month_start, last_month_end)

        # Score categories by size and growth
        scored = [
            {
                "category": cat["category"],
                "amount": cat["amount"],
                "growth": growth_rates.get(cat["category"], 0),
                "impact_score": cat["amount"] * (1 + growth_rates.get(cat["category"], 0) / 100),
            }
            for cat in categories
        ]

        scored.sort(key=lambda x: x["impact_score"], reverse=True)

        total_expenses = sum(cat["amount"] for cat in categories)

        return {
            "total_expenses": round(total_expenses, 2),
            "top_categories": scored[:5],
            "highest_growth": max(scored, key=lambda x: x["growth"])["category"] if scored else None,
            "highest_amount": scored[0]["category"] if scored else None,
        }

    def _get_expense_categories(self, start: datetime, end: datetime) -> List[Dict]:
        """Get expenses by category."""
        rows = (
            self.db.query(Transaction.category, func.sum(Transaction.amount).label("total"))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= start,
                Transaction.date <= end,
            )
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        return [
            {"category": row.category, "amount": float(row.total)}
            for row in rows
        ]

    def _calculate_growth_rates(
        self, current_cats: List[Dict], prev_start: datetime, prev_end: datetime
    ) -> Dict[str, float]:
        """Calculate month-over-month growth for each category."""
        growth = {}

        for cat in current_cats:
            cat_name = cat["category"]
            current_amt = cat["amount"]

            prev_result = (
                self.db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.user_id == self.user_id,
                    Transaction.type == TransactionType.expense,
                    Transaction.category == cat_name,
                    Transaction.date >= prev_start,
                    Transaction.date <= prev_end,
                )
                .scalar()
            )

            prev_amt = float(prev_result or 0)

            if prev_amt > 0:
                pct_change = ((current_amt - prev_amt) / prev_amt) * 100
                growth[cat_name] = pct_change
            elif current_amt > 0:
                growth[cat_name] = 100  # New category this month
            else:
                growth[cat_name] = 0

        return growth


class RiskDetectorEngine:
    """Identifies financial risks and red flags."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def analyze(self) -> Dict:
        """
        Detect financial risks.

        Returns: list of risks ranked by severity.
        """
        risks = []

        # Check cashflow
        cashflow_risk = self._check_cashflow_risk()
        if cashflow_risk:
            risks.append({"type": "cashflow", "severity": cashflow_risk["severity"], "message": cashflow_risk["message"]})

        # Check profitability
        profitability_risk = self._check_profitability_risk()
        if profitability_risk:
            risks.append({"type": "profitability", "severity": profitability_risk["severity"], "message": profitability_risk["message"]})

        # Check expense concentration
        concentration_risk = self._check_concentration_risk()
        if concentration_risk:
            risks.append({"type": "concentration", "severity": concentration_risk["severity"], "message": concentration_risk["message"]})

        # Sort by severity
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        risks.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return {
            "risk_count": len(risks),
            "risks": risks[:5],  # Top 5 risks
        }

    def _check_cashflow_risk(self) -> Optional[Dict]:
        """Check if business has cashflow risk."""
        balance = self._get_balance()
        daily_burn = self._get_daily_burn_rate()

        if daily_burn <= 0:
            return None

        if balance <= 0:
            return {"severity": "critical", "message": "Zero or negative cash balance"}

        days = balance / daily_burn
        if days < 30:
            return {"severity": "critical", "message": f"Only {int(days)} days of cash runway"}
        elif days < 90:
            return {"severity": "warning", "message": f"Cash runway declining ({int(days)} days left)"}

        return None

    def _check_profitability_risk(self) -> Optional[Dict]:
        """Check if business has profitability risk."""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        income = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.income,
                Transaction.date >= month_start,
                Transaction.date <= now,
            )
            .scalar()
        )

        expenses = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= month_start,
                Transaction.date <= now,
            )
            .scalar()
        )

        income = float(income or 0)
        expenses = float(expenses or 0)

        if income == 0:
            return {"severity": "critical", "message": "No revenue this month"}

        profit = income - expenses
        margin = (profit / income) * 100

        if profit < 0:
            return {"severity": "critical", "message": f"Operating at a loss (margin: {margin:.1f}%)"}
        elif margin < 10:
            return {"severity": "warning", "message": f"Thin profit margin ({margin:.1f}%)"}

        return None

    def _check_concentration_risk(self) -> Optional[Dict]:
        """Check if expenses are concentrated in one category."""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        rows = (
            self.db.query(Transaction.category, func.sum(Transaction.amount).label("total"))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= month_start,
                Transaction.date <= now,
            )
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        if not rows:
            return None

        total = sum(r.total for r in rows)
        top_category_pct = (rows[0].total / total) * 100 if total > 0 else 0

        if top_category_pct > 50:
            return {
                "severity": "warning",
                "message": f"{rows[0].category} accounts for {top_category_pct:.0f}% of expenses",
            }

        return None

    def _get_balance(self) -> float:
        """Get all-time net balance."""
        income = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.income,
            )
            .scalar()
        )
        expenses = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
            )
            .scalar()
        )
        return float(income or 0) - float(expenses or 0)

    def _get_daily_burn_rate(self, days: int = 30) -> float:
        """Average daily spending over last N days."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        total_expenses = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == self.user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )
        return float(total_expenses or 0) / days if days > 0 else 0.0
