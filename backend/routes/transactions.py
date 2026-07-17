from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.database import get_db
from models.models import User, Transaction, TransactionType
from middleware.auth import get_current_user
from middleware.subscription_guard import check_transaction_limit
from services.subscription_service import SubscriptionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: datetime
    description: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None


@router.post("/")
def create_transaction(
    req: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_transaction_limit)
):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    txn = Transaction(
        user_id=current_user.id,
        amount=req.amount,
        type=req.type,
        category=req.category,
        date=req.date,
        description=req.description
    )
    db.add(txn)
    
    # Increment monthly transaction count
    SubscriptionService.increment_transaction_count(db, current_user.id)
    
    db.commit()
    db.refresh(txn)
    return txn


@router.get("/")
def list_transactions(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    if type:
        q = q.filter(Transaction.type == type)
    if category:
        q = q.filter(Transaction.category == category)
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)

    total = q.count()
    items = q.order_by(Transaction.date.desc()).offset(offset).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{txn_id}")
def get_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == current_user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.put("/{txn_id}")
def update_transaction(
    txn_id: int,
    req: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == current_user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if req.amount is not None:
        txn.amount = req.amount
    if req.category is not None:
        txn.category = req.category
    if req.date is not None:
        txn.date = req.date
    if req.description is not None:
        txn.description = req.description

    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/{txn_id}")
def delete_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    txn = db.query(Transaction).filter(
        Transaction.id == txn_id,
        Transaction.user_id == current_user.id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()
    return {"message": "Transaction deleted"}
