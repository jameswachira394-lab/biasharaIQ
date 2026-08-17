from datetime import datetime, timedelta
import hashlib
import hmac
import os
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from middleware.auth import hash_password, verify_password, create_access_token
from models.database import get_db
from models.models import User, Category, TransactionType
from services.email_verification import generate_verification_code, send_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])

DEFAULT_EXPENSE_CATEGORIES = [
    "Rent", "Salaries", "Stock / Inventory", "Transport", "Utilities",
    "Marketing", "Equipment", "Food & Drinks", "Internet & Airtime",
    "Licenses & Permits", "Repairs & Maintenance", "Packaging",
    "Loan Repayment", "Other",
]

DEFAULT_INCOME_CATEGORIES = [
    "Product Sales", "Service Fees", "Delivery Income", "Commission",
    "Rental Income", "Online Sales", "Other",
]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    business_name: str
    owner_name: str = None
    phone: str = None
    business_type: str = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. Email verification required before login."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    code = generate_verification_code()

    # Create user with is_verified=False and verification code
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        business_name=req.business_name,
        owner_name=req.owner_name,
        phone=req.phone,
        business_type=req.business_type,
        is_verified=False,  # ✅ MUST be False
        verification_code=code,
        verification_expires_at=datetime.utcnow() + timedelta(minutes=10),
    )

    db.add(user)
    db.flush()  # Get user.id without committing

    # Create default categories
    for name in DEFAULT_EXPENSE_CATEGORIES:
        db.add(Category(user_id=user.id, name=name, type=TransactionType.expense, is_default=True))
    for name in DEFAULT_INCOME_CATEGORIES:
        db.add(Category(user_id=user.id, name=name, type=TransactionType.income, is_default=True))

    db.commit()
    db.refresh(user)

    # Send verification email
    email_sent = send_email(req.email, code)

    # ✅ NO ACCESS TOKEN - User must verify email first to get token
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "business_name": user.business_name,
            "owner_name": user.owner_name,
            "is_verified": False,  # Explicitly show not verified
        },
        "email_sent": email_sent,
        "message": "Account created. Check your email for the verification code." if email_sent else "Account created. Use code 123456 to verify (development mode).",
    }


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password. Email must be verified first."""
    user = db.query(User).filter(User.email == req.email).first()
    
    # Check credentials
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Check email verification
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please verify your email first.",
        )

    # Issue token only if verified
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
    }


# ─── Simple in-memory rate limiting for forgot-password ───────────────────────
# Maps email → list of request timestamps (UTC)
_reset_attempts: dict[str, list[datetime]] = {}
_RATE_LIMIT_MAX = 3          # max requests
_RATE_LIMIT_WINDOW = 3600    # per hour (seconds)
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://biasharaiq.netlify.app")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    email: EmailStr
    new_password: str


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send a password-reset link. Always returns a generic response to prevent
    user-enumeration attacks. Rate-limited to 3 requests per hour per email.
    """
    now = datetime.utcnow()
    email_lower = req.email.lower()

    # Rate-limit check
    attempts = _reset_attempts.get(email_lower, [])
    cutoff = now - timedelta(seconds=_RATE_LIMIT_WINDOW)
    attempts = [t for t in attempts if t > cutoff]  # drop old entries
    if len(attempts) >= _RATE_LIMIT_MAX:
        # Return generic message even when rate-limited to avoid leaking info
        return {
            "message": "If an account exists with this email address, you will receive a password reset link shortly."
        }
    attempts.append(now)
    _reset_attempts[email_lower] = attempts

    # Look up user without revealing existence
    user = db.query(User).filter(User.email == email_lower).first()
    if user:
        # Generate cryptographically secure token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        user.reset_token_hash = token_hash
        user.reset_token_expires_at = now + timedelta(minutes=15)
        db.commit()

        # Build reset link
        reset_link = f"{FRONTEND_URL}/reset-password?token={raw_token}&email={email_lower}"
        try:
            send_password_reset_email(email_lower, reset_link)
        except Exception:
            pass  # Never fail the response — email errors are logged internally

    return {
        "message": "If an account exists with this email address, you will receive a password reset link shortly."
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Validate reset token, hash and save new password, then invalidate token.
    """
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    email_lower = req.email.lower()
    user = db.query(User).filter(User.email == email_lower).first()

    # Constant-time token validation — always compute hash even if no user found
    incoming_hash = hashlib.sha256(req.token.encode()).hexdigest()
    dummy_hash = "0" * 64  # fallback for constant-time comparison when user not found

    stored_hash = user.reset_token_hash if user else dummy_hash
    token_valid = hmac.compare_digest(incoming_hash, stored_hash if stored_hash else dummy_hash)

    now = datetime.utcnow()
    expired = (
        not user
        or not user.reset_token_expires_at
        or user.reset_token_expires_at < now
    )

    if not token_valid or expired:
        raise HTTPException(
            status_code=400,
            detail="This password reset link is invalid or has expired. Please request a new one.",
        )

    # Update password and invalidate token
    user.password_hash = hash_password(req.new_password)
    user.reset_token_hash = None
    user.reset_token_expires_at = None
    db.commit()

    return {"message": "Your password has been reset successfully. You can now log in."}