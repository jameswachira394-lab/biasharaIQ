"""
BiasharaIQ Demo Seed Script
---------------------------
Creates a demo user account and populates realistic transaction data
for a Kenyan small business (a retail shop called "Mama Jane's General Store").

Usage:
    cd backend
    python seed_demo.py

    Or with a custom DATABASE_URL:
    DATABASE_URL=postgresql://... python seed_demo.py
"""

import os
import sys
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Must be run from the backend directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, engine
from models.models import Base, User, Transaction, Category, TransactionType
from middleware.auth import hash_password

# ─── Config ───────────────────────────────────────────────────────────────────

DEMO_EMAIL = "demo@biasharaiq.com"
DEMO_PASSWORD = "demo1234"
DEMO_BUSINESS = "Mama Jane's General Store"
DEMO_OWNER = "Jane Wanjiku"

INCOME_CATEGORIES = [
    "Product Sales", "Service Fees", "Delivery Income",
    "Commission", "Online Sales"
]

EXPENSE_CATEGORIES = [
    "Rent", "Salaries", "Stock / Inventory", "Transport", "Utilities",
    "Marketing", "Equipment", "Food & Drinks", "Internet & Airtime",
    "Packaging", "Loan Repayment", "Repairs & Maintenance", "Other"
]

# Realistic transaction templates for a Nairobi retail shop
INCOME_TEMPLATES = [
    ("Product Sales", 3500, 8000, "Daily sales"),
    ("Product Sales", 1200, 3500, "Morning sales"),
    ("Product Sales", 4000, 12000, "Weekend sales"),
    ("Service Fees", 500, 1500, "Delivery charge"),
    ("Online Sales", 800, 2500, "M-Pesa order"),
    ("Commission", 200, 800, "Agent commission"),
    ("Delivery Income", 300, 900, "Delivery fee"),
]

EXPENSE_TEMPLATES = [
    ("Stock / Inventory", 8000, 25000, "Stock restock"),
    ("Stock / Inventory", 3000, 8000, "Supplies top-up"),
    ("Rent", 15000, 15000, "Monthly rent"),
    ("Salaries", 12000, 12000, "Staff salary"),
    ("Transport", 300, 800, "Matatu fare / delivery"),
    ("Utilities", 800, 1200, "Electricity bill"),
    ("Utilities", 200, 500, "Water bill"),
    ("Internet & Airtime", 500, 1000, "Airtime & data"),
    ("Marketing", 500, 2000, "Flyers / social media"),
    ("Food & Drinks", 200, 600, "Staff meals"),
    ("Packaging", 300, 700, "Bags and packaging"),
    ("Loan Repayment", 5000, 5000, "Equity Bank loan"),
    ("Repairs & Maintenance", 500, 3000, "Equipment repair"),
    ("Other", 100, 500, "Miscellaneous"),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── User ──────────────────────────────────────────────────────────────
        existing = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if existing:
            print(f"⚠  Demo user already exists ({DEMO_EMAIL}). Skipping user creation.")
            user = existing
        else:
            user = User(
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                business_name=DEMO_BUSINESS,
                owner_name=DEMO_OWNER,
                phone="+254 712 345 678",
                business_type="Retail Shop",
            )
            db.add(user)
            db.flush()

            # Default categories
            for name in EXPENSE_CATEGORIES:
                db.add(Category(user_id=user.id, name=name, type=TransactionType.expense, is_default=True))
            for name in INCOME_CATEGORIES:
                db.add(Category(user_id=user.id, name=name, type=TransactionType.income, is_default=True))

            db.commit()
            print(f"✓  Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        # ── Transactions ──────────────────────────────────────────────────────
        existing_count = db.query(Transaction).filter(Transaction.user_id == user.id).count()
        if existing_count > 0:
            print(f"⚠  {existing_count} transactions already exist. Skipping transaction seed.")
        else:
            now = datetime.utcnow()
            transactions = []

            # Generate 90 days of data
            for day_offset in range(90, 0, -1):
                date = now - timedelta(days=day_offset)
                weekday = date.weekday()  # 0=Mon, 6=Sun

                # Income: 2-5 entries per day (more on weekends)
                income_count = random.randint(3, 6) if weekday >= 5 else random.randint(2, 4)
                for _ in range(income_count):
                    cat, low, high, desc = random.choice(INCOME_TEMPLATES)
                    # Slow months have lower income
                    multiplier = 0.75 if day_offset > 60 else 1.0
                    amount = round(random.uniform(low * multiplier, high * multiplier), -1)
                    transactions.append(Transaction(
                        user_id=user.id,
                        amount=amount,
                        type=TransactionType.income,
                        category=cat,
                        date=date.replace(hour=random.randint(8, 20), minute=random.randint(0, 59)),
                        description=desc,
                    ))

                # Expenses: 1-3 per day
                expense_count = random.randint(1, 3)
                for _ in range(expense_count):
                    cat, low, high, desc = random.choice(EXPENSE_TEMPLATES)
                    amount = round(random.uniform(low, high), -1)
                    transactions.append(Transaction(
                        user_id=user.id,
                        amount=amount,
                        type=TransactionType.expense,
                        category=cat,
                        date=date.replace(hour=random.randint(8, 18), minute=random.randint(0, 59)),
                        description=desc,
                    ))

                # Monthly fixed costs on day 1
                if date.day == 1:
                    for cat, amount, desc in [
                        ("Rent", 15000, "Monthly rent - Ngara stall"),
                        ("Salaries", 12000, "Employee salary - Kamau"),
                        ("Loan Repayment", 5000, "Equity Bank microfinance"),
                    ]:
                        transactions.append(Transaction(
                            user_id=user.id, amount=amount,
                            type=TransactionType.expense, category=cat,
                            date=date.replace(hour=9, minute=0), description=desc,
                        ))

            db.bulk_save_objects(transactions)
            db.commit()
            print(f"✓  Created {len(transactions)} transactions spanning 90 days")

        # ── Summary ───────────────────────────────────────────────────────────
        from sqlalchemy import func
        income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.income
        ).scalar() or 0
        expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.expense
        ).scalar() or 0

        print("\n── Demo Account Summary ───────────────────────────")
        print(f"   Email:      {DEMO_EMAIL}")
        print(f"   Password:   {DEMO_PASSWORD}")
        print(f"   Business:   {DEMO_BUSINESS}")
        print(f"   Total In:   KES {income:,.0f}")
        print(f"   Total Out:  KES {expenses:,.0f}")
        print(f"   Net Profit: KES {income - expenses:,.0f}")
        print("────────────────────────────────────────────────────")
        print("\n✓  Seed complete. Start the server and log in with the credentials above.")

    except Exception as e:
        db.rollback()
        print(f"✗  Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
