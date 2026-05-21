from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from services.email_verification import generate_verification_code, send_email
from models.database import get_db
from models.models import User
from middleware.auth import create_access_token
from core.config import settings

router = APIRouter(tags=["Email Verification"])

MASTER_CODE = "123456"


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str


def _is_code_valid(user: User, code: str) -> bool:
    """Return True if the submitted code is acceptable for this user."""
    real_code_valid = (
        user.verification_code is not None
        and user.verification_code == code
        and user.verification_expires_at is not None
        and datetime.utcnow() <= user.verification_expires_at
    )
    if real_code_valid:
        return True

    # Master bypass — development only, never in production
    if settings.DEBUG and not settings.IS_PRODUCTION and code == MASTER_CODE:
        return True

    return False


@router.post("/send-verification")
def send_verification(data: EmailRequest, db: Session = Depends(get_db)):
    """Send a verification code to the given email address."""
    user = db.query(User).filter(User.email == data.email).first()

    # Return 200 even for unknown emails to prevent user enumeration
    if not user or user.is_verified:
        return {"message": "If this email is registered and unverified, a code has been sent."}

    code = generate_verification_code()
    user.verification_code = code
    user.verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    send_email(data.email, code)  # Failure is logged in send_email; don't leak status to caller

    return {"message": "If this email is registered and unverified, a code has been sent."}


@router.post("/verify-email")
def verify_email(data: VerifyRequest, db: Session = Depends(get_db)):
    """Verify email with the provided code and issue an access token."""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    if not _is_code_valid(user, data.code):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    user.is_verified = True
    user.verification_code = None
    user.verification_expires_at = None
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "business_name": user.business_name,
            "owner_name": user.owner_name,
            "is_verified": True,
        },
        "message": "Email verified successfully. You are now logged in.",
    }