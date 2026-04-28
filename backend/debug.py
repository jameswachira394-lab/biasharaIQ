#!/usr/bin/env python
"""
Comprehensive system debug script for BiasharaIQ
Tests all components and identifies issues
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("BIASHARAIQ SYSTEM DEBUG")
print("=" * 60)

# 1. Environment Check
print("\n[INFO] ENVIRONMENT VARIABLES")
print("-" * 60)
required_vars = ['DATABASE_URL', 'SECRET_KEY', 'ALGORITHM', 'GEMINI_API_KEY']
for var in required_vars:
    value = os.getenv(var, "NOT SET")
    masked = value[:20] + "..." if len(value) > 20 else value
    status = "[OK]" if value != "NOT SET" else "[FAIL]"
    print(f"{status} {var}: {masked}")

# 2. Database Connection Check
print("\n[INFO] DATABASE CONNECTION")
print("-" * 60)
try:
    from models.database import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    result = db.execute(text("SELECT 1"))
    print("[OK] Database connection successful")
    db.close()
except Exception as e:
    print(f"[FAIL] Database connection failed: {e}")
    sys.exit(1)

# 3. Models Check
print("\n[INFO] MODELS VERIFICATION")
print("-" * 60)
try:
    from models.models import User, Transaction, Category, Insight, TransactionType
    print("[OK] All models imported successfully")
    print(f"  - User model")
    print(f"  - Transaction model")
    print(f"  - Category model")
    print(f"  - Insight model")
    print(f"  - TransactionType enum: {list(TransactionType)}")
except Exception as e:
    print(f"[FAIL] Model import failed: {e}")
    sys.exit(1)

# 4. Authentication Check
print("\n[INFO] AUTHENTICATION SYSTEM")
print("-" * 60)
try:
    from middleware.auth import hash_password, verify_password, create_access_token, get_current_user
    # Test password hashing
    test_pass = "test123password"
    hashed = hash_password(test_pass)
    verified = verify_password(test_pass, hashed)
    print(f"[OK] Password hashing works: {verified}")
    
    # Test token creation
    token = create_access_token({"sub": 1})
    print(f"[OK] Token creation works: {token[:30]}...")
    print(f"[OK] Token length: {len(token)} bytes")
except Exception as e:
    print(f"[FAIL] Authentication failed: {e}")
    sys.exit(1)

# 5. Routes Check
print("\n[INFO] ROUTES VERIFICATION")
print("-" * 60)
try:
    from routes.auth import router as auth_router
    from routes.transactions import router as transactions_router
    from routes.routes import (
        dashboard_router, insights_router, ai_router,
        reports_router, categories_router, profile_router
    )
    print("[OK] All routers imported successfully")
    routers = [
        ("Auth", auth_router),
        ("Transactions", transactions_router),
        ("Dashboard", dashboard_router),
        ("Insights", insights_router),
        ("AI", ai_router),
        ("Reports", reports_router),
        ("Categories", categories_router),
        ("Profile", profile_router),
    ]
    for name, router in routers:
        print(f"  - {name} router: {len(router.routes)} routes")
except Exception as e:
    print(f"[FAIL] Router import failed: {e}")
    sys.exit(1)

# 6. Services Check
print("\n[INFO] SERVICES VERIFICATION")
print("-" * 60)
try:
    from services.financial_engine import FinancialEngine
    from services.insights_engine import InsightsEngine
    from services.ai_agent import chat_with_ai_agent
    print("[OK] All services imported successfully")
    print(f"  - Financial Engine")
    print(f"  - Insights Engine")
    print(f"  - AI Agent")
except Exception as e:
    print(f"[FAIL] Service import failed: {e}")
    sys.exit(1)

# 7. Dependencies Check
print("\n[INFO] DEPENDENCIES CHECK")
print("-" * 60)
try:
    import fastapi
    import sqlalchemy
    import pydantic
    import passlib
    import bcrypt
    import jose
    from google import genai
    
    deps = [
        ("FastAPI", fastapi.__version__),
        ("SQLAlchemy", sqlalchemy.__version__),
        ("Pydantic", pydantic.__version__),
        ("Passlib", passlib.__version__),
        ("Bcrypt", bcrypt.__version__),
        ("python-jose", jose.__version__),
    ]
    for name, version in deps:
        print(f"[OK] {name}: {version}")
except Exception as e:
    print(f"[FAIL] Dependency check failed: {e}")
    sys.exit(1)

# 8. Database Schema Check
print("\n[INFO] DATABASE SCHEMA")
print("-" * 60)
try:
    db = SessionLocal()
    users = db.query(User).count()
    transactions = db.query(Transaction).count()
    categories = db.query(Category).count()
    print(f"[OK] Database tables exist and are queryable")
    print(f"  - Users: {users}")
    print(f"  - Transactions: {transactions}")
    print(f"  - Categories: {categories}")
    db.close()
except Exception as e:
    print(f"[FAIL] Schema check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] ALL SYSTEMS OPERATIONAL")
print("=" * 60)
