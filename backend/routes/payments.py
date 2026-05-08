from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models.database import get_db
from models.models import User, Payment, UserPlan
from services.mpesa import MpesaService
from services.subscription_service import SubscriptionService
from middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["Payments"])
mpesa_service = MpesaService()

class PaymentInitiateRequest(BaseModel):
    phone: str
    amount: int = 499  # Default Pro Plan price

@router.post("/initiate")
async def initiate_payment(
    req: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiate M-Pesa STK Push for PRO upgrade."""
    logger.info(f"Initiating payment for user {current_user.id} - {req.phone}")
    
    # Initiate STK Push
    response = mpesa_service.initiate_stk_push(
        phone=req.phone,
        amount=req.amount,
        account_ref=f"User-{current_user.id}"
    )
    
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    
    checkout_id = response.get("CheckoutRequestID")
    merchant_id = response.get("MerchantRequestID")
    
    if not checkout_id:
        raise HTTPException(status_code=500, detail="Failed to get CheckoutRequestID from M-Pesa")

    # Save payment record
    payment = Payment(
        user_id=current_user.id,
        phone_number=req.phone,
        amount=float(req.amount),
        checkout_request_id=checkout_id,
        merchant_request_id=merchant_id,
        status="pending"
    )
    db.add(payment)
    db.commit()
    
    return {
        "checkout_id": checkout_id,
        "message": response.get("CustomerMessage", "STK Push initiated")
    }

@router.post("/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    """Callback endpoint for M-Pesa to report transaction results."""
    data = await request.json()
    logger.info(f"Received M-Pesa callback: {data}")
    
    result = mpesa_service.verify_callback(data)
    checkout_id = result.get("checkout_id")
    
    payment = db.query(Payment).filter(Payment.checkout_request_id == checkout_id).first()
    if not payment:
        logger.error(f"Payment record not found for checkout_id: {checkout_id}")
        return {"status": "ok"}

    if result.get("success"):
        payment.status = "completed"
        payment.mpesa_receipt = result.get("receipt")
        
        # Upgrade the user
        SubscriptionService.upgrade_user(
            db=db,
            user_id=payment.user_id,
            plan=UserPlan.pro,
            amount=payment.amount
        )
        logger.info(f"Payment {checkout_id} successful. User {payment.user_id} upgraded.")
    else:
        payment.status = "failed"
        logger.warning(f"Payment {checkout_id} failed: {result.get('message')}")
        
    db.commit()
    return {"status": "ok"}

@router.get("/status/{checkout_id}")
async def get_payment_status(
    checkout_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check status of a payment."""
    payment = db.query(Payment).filter(
        Payment.checkout_request_id == checkout_id,
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    return {
        "status": payment.status,
        "amount": payment.amount,
        "receipt": payment.mpesa_receipt,
        "created_at": payment.created_at
    }
