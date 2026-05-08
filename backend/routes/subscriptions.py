from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User, UserPlan
from services.subscription_service import SubscriptionService
from middleware.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/subscription", tags=["Subscription"])

@router.get("/status")
async def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user subscription status and usage."""
    # Check if expired and update status
    user = SubscriptionService.check_and_update_status(db, current_user.id)
    
    return {
        "plan": user.plan,
        "status": user.subscription_status,
        "expires_at": user.subscription_end,
        "is_pro": user.plan == UserPlan.pro,
        "usage": {
            "current": user.monthly_transaction_count,
            "limit": 200 if user.plan == UserPlan.free else None,
            "percentage": (user.monthly_transaction_count / 200 * 100) if user.plan == UserPlan.free else 0
        },
        "days_remaining": (user.subscription_end - datetime.utcnow()).days if user.subscription_end else None
    }

@router.get("/plans")
async def get_plans():
    """Get available plans and features."""
    return [
        {
            "id": "free",
            "name": "Free Plan",
            "price": 0,
            "features": [
                "Track up to 200 transactions/month",
                "Basic dashboard & profit view",
                "Expense categories",
                "Email support"
            ],
            "limitations": [
                "Max 200 transactions/month",
                "No AI Assistant",
                "No predictions",
                "No smart insights"
            ]
        },
        {
            "id": "pro",
            "name": "Pro Plan",
            "price": 499,
            "features": [
                "Unlimited transactions",
                "AI Assistant",
                "Cash flow predictions",
                "Smart insights & waste detection",
                "Days remaining forecast + alerts",
                "Priority support"
            ]
        }
    ]
