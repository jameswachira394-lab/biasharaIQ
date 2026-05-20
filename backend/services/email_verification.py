from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from core.config import settings
from models.database import get_db
from models.models import User
from services.email_verification import generate_verification_code, send_email

router = APIRouter(prefix="/auth", tags=["Email Verification"])


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str


@router.post("/send-verification")
def send_verification(data: EmailRequest, db: Session = Depends(get_db)):
    """Resend verification code to email"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    code = generate_verification_code()
    user.verification_code = code
    user.verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()  # ✅ single commit, no prior split state here

    email_sent = send_email(data.email, code)
    if not email_sent:
        print(f"[AUTH] Warning: Failed to send verification email to {data.email}")

    return {"message": "Verification code sent to email", "email": data.email}


@router.post("/verify-email")
def verify_email(data: VerifyRequest, db: Session = Depends(get_db)):
    """Verify email with the provided code"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Guard None fields before comparing to avoid TypeError
    if user.verification_code is None:
        raise HTTPException(status_code=400, detail="No verification pending")

    if user.verification_expires_at is None or datetime.utcnow() > user.verification_expires_at:
        raise HTTPException(status_code=400, detail="Verification code has expired")

    code_matches = user.verification_code == data.code
    debug_bypass = settings.DEBUG and data.code == "123456"

    if not code_matches and not debug_bypass:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user.is_verified = True
    user.verification_code = None
    user.verification_expires_at = None
    db.commit()

    return {"message": "Email verified successfully"}