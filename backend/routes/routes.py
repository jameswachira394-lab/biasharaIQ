from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from models.database import get_db
from models.models import User, Category, Insight, TransactionType
from middleware.auth import get_current_user
from services.financial_engine import FinancialEngine
from services.insights_engine import InsightsEngine
from services.ai_agent import chat_with_ai_agent
from middleware.subscription_guard import require_pro

# ──────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = FinancialEngine(db, current_user.id)
    metrics = engine.get_full_metrics()
    insights_engine = InsightsEngine(db, current_user.id)
    insights = insights_engine.generate_insights()
    trend = engine.get_weekly_trend(8)

    return {
        "business_name": current_user.business_name,
        "owner_name": current_user.owner_name,
        "metrics": metrics,
        "insights": insights,
        "weekly_trend": trend
    }



insights_router = APIRouter(prefix="/insights", tags=["insights"])


@insights_router.get("/", dependencies=[Depends(require_pro)])
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = InsightsEngine(db, current_user.id)
    return engine.generate_insights()


@insights_router.get("/history")
def get_insight_history(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pro)
):
    items = (
        db.query(Insight)
        .filter(Insight.user_id == current_user.id)
        .order_by(Insight.timestamp.desc())
        .limit(limit)
        .all()
    )
    return items


# ──────────────────────────────────────────────
# AI Agent
# ──────────────────────────────────────────────
ai_router = APIRouter(prefix="/ai", tags=["ai"])


class ChatMessage(BaseModel):
    message: str
    history: Optional[List[dict]] = []


@ai_router.post("/chat")
def chat(
    req: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pro)
):
    try:
        response = chat_with_ai_agent(
            db=db,
            user_id=current_user.id,
            business_name=current_user.business_name,
            user_message=req.message,
            conversation_history=req.history
        )
        return {"response": response}
    except ValueError as e:
        if "API key" in str(e):
            return {"error": str(e)}, 500
        raise
    except Exception as e:
        print(f"AI Chat Error: {str(e)}")
        # If it's a known error from our ai_agent.py, it will have a clear message
        return {"error": str(e)}, 500


# ──────────────────────────────────────────────
# Reports
# ──────────────────────────────────────────────
reports_router = APIRouter(prefix="/reports", tags=["reports"])


@reports_router.get("/monthly")
def monthly_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = FinancialEngine(db, current_user.id)
    summary = engine.get_monthly_summary()
    expense_breakdown = engine.get_category_breakdown("expense")
    income_breakdown = engine.get_category_breakdown("income")
    trend = engine.get_weekly_trend(4)
    return {
        "summary": summary,
        "expense_breakdown": expense_breakdown,
        "income_breakdown": income_breakdown,
        "weekly_trend": trend
    }


@reports_router.get("/weekly-trend")
def weekly_trend(
    weeks: int = Query(8, le=52),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = FinancialEngine(db, current_user.id)
    return engine.get_weekly_trend(weeks)


# ──────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────
categories_router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    name: str
    type: TransactionType
    icon: Optional[str] = None


@categories_router.get("/")
def list_categories(
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Category).filter(Category.user_id == current_user.id)
    if type:
        q = q.filter(Category.type == type)
    return q.all()


@categories_router.post("/")
def create_category(
    req: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cat = Category(
        user_id=current_user.id,
        name=req.name,
        type=req.type,
        icon=req.icon,
        is_default=False
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@categories_router.delete("/{cat_id}")
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cat = db.query(Category).filter(
        Category.id == cat_id,
        Category.user_id == current_user.id,
        Category.is_default == False
    ).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found or cannot delete a default category")
    db.delete(cat)
    db.commit()
    return {"message": "Deleted"}


# ──────────────────────────────────────────────
# User Profile
# ──────────────────────────────────────────────
profile_router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    business_type: Optional[str] = None


@profile_router.get("/")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "business_name": current_user.business_name,
        "owner_name": current_user.owner_name,
        "phone": current_user.phone,
        "business_type": current_user.business_type,
        "created_at": current_user.created_at,
        "plan": current_user.plan,
        "subscription_status": current_user.subscription_status,
        "subscription_end": current_user.subscription_end,
        "monthly_transaction_count": current_user.monthly_transaction_count
    }


@profile_router.put("/")
def update_profile(
    req: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if req.business_name:
        current_user.business_name = req.business_name
    if req.owner_name:
        current_user.owner_name = req.owner_name
    if req.phone:
        current_user.phone = req.phone
    if req.business_type:
        current_user.business_type = req.business_type
    db.commit()
    return {"message": "Profile updated"}
