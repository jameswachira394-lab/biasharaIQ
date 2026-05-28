#!/usr/bin/env python3
"""
M-Pesa B2B Integration Test
Tests payments routes, B2B payment initiation, and callbacks.
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import FastAPI app and database components
from backend.main import app
from backend.models.database import get_db, Base
from backend.models.models import User, Payment, UserPlan
from backend.middleware.auth import get_current_user
from backend.services.mpesa import MpesaService

# Create an in-memory SQLite engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_b2b.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestMpesaB2BIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create SQLite tables
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()
        
        # Create test user
        cls.test_user = User(
            email="test_b2b_user@biasharaiq.com",
            password_hash="fake_hash",
            business_name="Test B2B Business",
            plan=UserPlan.free,
            is_active=True,
            is_verified=True
        )
        cls.db.add(cls.test_user)
        cls.db.commit()
        cls.db.refresh(cls.test_user)
        
    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_b2b.db"):
            os.remove("./test_b2b.db")

    def setUp(self):
        # Override dependencies
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
                
        def override_get_current_user():
            # Always return our test user
            db = TestingSessionLocal()
            user = db.query(User).filter(User.id == self.test_user.id).first()
            db.close()
            return user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    @patch('backend.routes.payments.mpesa_service')
    def test_01_initiate_b2b_payment(self, mock_mpesa_service):
        # 1. Setup mock response from Safaricom B2B API
        mock_mpesa_service.initiate_b2b_payment_request.return_value = {
            "ConversationID": "AG_20260528_B2BTESTCONV_ID",
            "OriginatorConversationID": "ORIG_B2BTEST_ID",
            "ResponseCode": "0",
            "ResponseDescription": "Accept the service request successfully."
        }

        # 2. Make the HTTP request to initiate B2B payment
        payload = {
            "sender_shortcode": "600000",
            "amount": 499,
            "initiator_name": "testapi",
            "security_credential": "fake_credential"
        }
        response = self.client.post("/payments/initiate-b2b", json=payload)
        
        # 3. Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["checkout_id"], "AG_20260528_B2BTESTCONV_ID")
        self.assertEqual(data["message"], "Accept the service request successfully.")
        
        # 4. Check if payment record was created in the database
        db = TestingSessionLocal()
        payment = db.query(Payment).filter(
            Payment.checkout_request_id == "AG_20260528_B2BTESTCONV_ID"
        ).first()
        db.close()
        
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.amount, 499.0)
        self.assertEqual(payment.phone_number, "B2B-600000")

    @patch('backend.routes.payments.mpesa_service')
    def test_02_b2b_callback_success(self, mock_mpesa_service):
        # 1. Prepare mock callback processing result
        mock_mpesa_service.verify_b2b_callback.return_value = {
            "success": True,
            "checkout_id": "AG_20260528_B2BTESTCONV_ID",
            "merchant_id": "ORIG_B2BTEST_ID",
            "receipt": "LK12345678",
            "amount": 499.0,
            "date": "20260528162000"
        }
        
        # 2. Make POST callback call
        callback_payload = {
            "Result": {
                "ResultType": 0,
                "ResultCode": 0,
                "ResultDesc": "Success",
                "ConversationID": "AG_20260528_B2BTESTCONV_ID",
                "OriginatorConversationID": "ORIG_B2BTEST_ID",
                "TransactionID": "LK12345678"
            }
        }
        
        response = self.client.post("/payments/b2b-callback", json=callback_payload)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        
        # 3. Verify database updates
        db = TestingSessionLocal()
        # Verify payment status
        payment = db.query(Payment).filter(
            Payment.checkout_request_id == "AG_20260528_B2BTESTCONV_ID"
        ).first()
        
        # Verify user upgrade
        user = db.query(User).filter(User.id == self.test_user.id).first()
        db.close()
        
        self.assertEqual(payment.status, "completed")
        self.assertEqual(payment.mpesa_receipt, "LK12345678")
        self.assertEqual(user.plan, UserPlan.pro)

    def test_03_payment_status_check(self):
        # 1. Get status for our payment record
        response = self.client.get("/payments/status/AG_20260528_B2BTESTCONV_ID")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["amount"], 499.0)
        self.assertEqual(data["receipt"], "LK12345678")


if __name__ == "__main__":
    unittest.main()
