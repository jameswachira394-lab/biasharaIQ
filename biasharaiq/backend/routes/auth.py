from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from models.database import get_db
from models.models import User, Category, TransactionType
from middleware.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

DEFAULT_EXPENSE_CATEGORIES = [
    "Rent", "Salaries", "Stock / Inventory", "Transport", "Utilities",
    "Marketing", "Equipment", "Food & Drinks", "Internet & Airtime",
    "Licenses & Permits", "Repairs & Maintenance", "Packaging",
    "Loan Repayment", "Other"
]

DEFAULT_INCOME_CATEGORIES = [
    "Product Sales", "Service Fees", "Delivery Income", "Commission",
    "Rental Income", "Online Sales", "Other"
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
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        business_name=req.business_name,
        owner_name=req.owner_name,
        phone=req.phone,
        business_type=req.business_type,
    )
    db.add(user)
    db.flush()

    # Seed default categories
    for name in DEFAULT_EXPENSE_CATEGORIES:
        db.add(Category(user_id=user.id, name=name, type=TransactionType.expense, is_default=True))
    for name in DEFAULT_INCOME_CATEGORIES:
        db.add(Category(user_id=user.id, name=name, type=TransactionType.income, is_default=True))

    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "business_name": user.business_name,
            "owner_name": user.owner_name
        }
    }


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "business_name": user.business_name,
            "owner_name": user.owner_name
        }
    }
