from openai import OpenAI
import os
from sqlalchemy.orm import Session
from services.financial_engine import FinancialEngine
from services.insights_engine import InsightsEngine
from models.models import Transaction
from datetime import datetime, timedelta
import json

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")


def build_financial_context(db: Session, user_id: int, business_name: str) -> str:
    """Build a rich financial context string for the AI agent."""
    engine = FinancialEngine(db, user_id)
    insights_engine = InsightsEngine(db, user_id)

    metrics = engine.get_full_metrics()
    insights = insights_engine.generate_insights()
    trend = engine.get_weekly_trend(weeks=4)

    # Recent transactions (last 20)
    recent_txns = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc())
        .limit(20)
        .all()
    )
    txn_list = [
        f"- {t.date.strftime('%d %b')}: {t.type.value.upper()} KES {t.amount:,.0f} [{t.category}] {t.description or ''}"
        for t in recent_txns
    ]

    context = f"""
=== BIASHARAIQ FINANCIAL DATA: {business_name} ===

ALL-TIME TOTALS:
- Total Money In: KES {metrics['all_time']['income']:,.2f}
- Total Money Out: KES {metrics['all_time']['expenses']:,.2f}
- Net Profit: KES {metrics['all_time']['profit']:,.2f}

THIS MONTH ({metrics['this_month'].get('month', 'Current Month')}):
- Money In: KES {metrics['this_month']['income']:,.2f}
- Money Out: KES {metrics['this_month']['expenses']:,.2f}
- Profit: KES {metrics['this_month']['profit']:,.2f}
- Profit Margin: {metrics['this_month']['profit_margin']}%

CASH FLOW:
- Daily Spending Rate: KES {metrics['cash_flow']['daily_spending_rate']:,.2f}/day
- Cash Runway: {metrics['cash_flow']['survival_days']} days
- Risk Level: {metrics['cash_flow']['risk_level'].upper()}

TOP EXPENSE CATEGORIES (this month):
{json.dumps(metrics['expense_breakdown'], indent=2)}

TOP INCOME SOURCES (this month):
{json.dumps(metrics['income_breakdown'], indent=2)}

RECENT TRANSACTIONS (last 20):
{chr(10).join(txn_list) if txn_list else "No transactions yet."}

ACTIVE SYSTEM INSIGHTS:
{chr(10).join([f"- [{i['severity'].upper()}] {i['message']}" for i in insights]) if insights else "No alerts at this time."}

4-WEEK TREND:
{json.dumps(trend, indent=2)}
"""
    return context


def chat_with_ai_agent(
    db: Session,
    user_id: int,
    business_name: str,
    user_message: str,
    conversation_history: list = None
) -> str:
    """
    BiasharaIQ AI Agent - responds based purely on the user's real financial data.
    No hallucinations. No generic advice. Data-driven only.
    """
    financial_context = build_financial_context(db, user_id, business_name)

    system_prompt = f"""You are BiasharaIQ AI, a financial intelligence assistant for small and medium businesses in Kenya.

Your role is to help the business owner understand their finances, identify problems, and make better decisions.

CRITICAL RULES:
1. ONLY use the financial data provided below. Never make up numbers.
2. Give SPECIFIC, ACTIONABLE advice based on the actual data.
3. Use simple language. Avoid accounting jargon. Say "Money In" not "Revenue".
4. Reference actual numbers from their data in every response.
5. If data is insufficient, say so clearly and suggest what to track.
6. Be direct and honest - if the business is losing money, say so clearly.
7. Keep responses concise (3-6 sentences for simple questions, more for complex ones).
8. Speak in Kenyan business context - reference KES, M-Pesa if relevant.

{financial_context}

Remember: You are their financial advisor, not a chatbot. Every insight must be grounded in their actual numbers above."""

    messages = [
        {"role": "system", "content": system_prompt}
    ]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=1000,
        messages=messages
    )

    return response.choices[0].message.content
