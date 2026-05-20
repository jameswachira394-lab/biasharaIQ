from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from services.email_verification import (
    generate_verification_code,
    send_email,
)
from models.database import get_db
from models.models import User

router = APIRouter(prefix="/auth", tags=["Email Verification"])


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str


@router.post("/send-verification")
def send_verification(data: EmailRequest, db: Session = Depends(get_db)):
    """Send verification code to email"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    from datetime import datetime, timedelta
    code = generate_verification_code()
    user.verification_code = code
    user.verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    send_email(data.email, code)

    return {"message": "Verification code sent to email", "email": data.email}


@router.post("/verify-email")
def verify_email(data: VerifyRequest, db: Session = Depends(get_db)):
    """Verify email with the provided code"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from datetime import datetime
    is_valid = False
    if user.verification_code == data.code and user.verification_expires_at and datetime.utcnow() <= user.verification_expires_at:
        is_valid = True
        
    # Allow master code '123456' in development mode
    from core.config import settings
    if settings.DEBUG and data.code == "123456":
        is_valid = True

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user.is_verified = True
    user.verification_code = None
    user.verification_expires_at = None
    db.commit()

    return {"message": "Email verified successfully"}
