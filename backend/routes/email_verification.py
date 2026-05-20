from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from services.email_verification import (
    generate_verification_code,
    store_verification_code,
    verify_code,
    send_email,
    clear_verification_code,
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

    code = generate_verification_code()
    store_verification_code(data.email, code)
    send_email(data.email, code)

    return {"message": "Verification code sent to email", "email": data.email}


@router.post("/verify-email")
def verify_email(data: VerifyRequest, db: Session = Depends(get_db)):
    """Verify email with the provided code"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_code(data.email, data.code):
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user.is_verified = True
    db.commit()
    clear_verification_code(data.email)

    return {"message": "Email verified successfully"}
