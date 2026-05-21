from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from middleware.auth import hash_password, verify_password, create_access_token
from models.database import get_db
from models.models import User, Category, TransactionType
from services.email_verification import generate_verification_code, send_email

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