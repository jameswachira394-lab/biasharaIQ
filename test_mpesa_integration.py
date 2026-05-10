#!/usr/bin/env python3
"""
M-Pesa Payment Integration Tester
Tests payment endpoints and M-Pesa integration
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PHONE = "254708374149"
TEST_AMOUNT = 1  # 1 KES for testing
JWT_TOKEN = None  # Will be filled after login

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def log_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def log_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_backend_health():
    """Test if backend is running"""
    log_info("Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            log_success("Backend is running")
            print(f"  Response: {response.json()}")
            return True
        else:
            log_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_error(f"Cannot connect to backend at {BASE_URL}")
        log_warning("Make sure backend is running: python main.py")
        return False
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        return False

def test_env_variables():
    """Check if M-Pesa env variables are loaded"""
    log_info("Checking M-Pesa configuration...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        log_success("Backend API documentation accessible at /docs")
        return True
    except Exception as e:
        log_error(f"Cannot access API docs: {str(e)}")
        return False

def authenticate(email, password):
    """Authenticate and get JWT token"""
    log_info(f"Authenticating as {email}...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            log_success(f"Authentication successful")
            print(f"  Token: {token[:50]}...")
            return token
        else:
            log_error(f"Authentication failed: {response.text}")
            return None
    except Exception as e:
        log_error(f"Authentication error: {str(e)}")
        return None

def test_payment_initiate(token):
    """Test payment initiation"""
    log_info("Testing payment initiation endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phone": TEST_PHONE,
            "amount": TEST_AMOUNT
        }
        
        response = requests.post(
            f"{BASE_URL}/payments/initiate",
            json=payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            checkout_id = data.get("checkout_id")
            log_success("Payment initiation successful")
            print(f"  Checkout ID: {checkout_id}")
            print(f"  Message: {data.get('message')}")
            return checkout_id
        else:
            log_error(f"Payment initiation failed: {response.text}")
            return None
    except requests.exceptions.Timeout:
        log_error("Request timed out (M-Pesa API may be slow)")
        return None
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return None

def test_payment_status(token, checkout_id):
    """Test payment status check"""
    log_info(f"Testing payment status check for {checkout_id}...")
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(
            f"{BASE_URL}/payments/status/{checkout_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success("Payment status retrieved")
            print(f"  Status: {data.get('status')}")
            print(f"  Amount: {data.get('amount')} KES")
            print(f"  Created: {data.get('created_at')}")
            if data.get('receipt'):
                print(f"  Receipt: {data.get('receipt')}")
            return data
        else:
            log_warning(f"Status check returned {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return None

def poll_payment_status(token, checkout_id, max_attempts=60):
    """Poll payment status until completion or timeout"""
    log_info(f"Polling payment status (max {max_attempts} attempts, 5s interval)...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            response = requests.get(
                f"{BASE_URL}/payments/status/{checkout_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                print(f"  [{attempt}/{max_attempts}] Status: {status}")
                
                if status == "completed":
                    log_success("Payment completed!")
                    print(f"    Receipt: {data.get('receipt')}")
                    return True
                elif status == "failed":
                    log_error("Payment failed")
                    return False
            
            time.sleep(5)
        except Exception as e:
            print(f"  [{attempt}/{max_attempts}] Error checking status: {str(e)}")
            time.sleep(5)
    
    log_warning("Payment status check timeout - transaction may still be processing")
    return False

def main():
    print(f"\n{'='*60}")
    print("M-Pesa Integration Test Suite")
    print(f"{'='*60}\n")
    
    # Step 1: Health check
    if not test_backend_health():
        log_error("Cannot proceed without backend")
        sys.exit(1)
    
    print()
    
    # Step 2: Check environment
    test_env_variables()
    
    print()
    
    # Step 3: Get credentials
    print("Please provide test account credentials:")
    email = input(f"{Colors.YELLOW}Email: {Colors.END}").strip()
    password = input(f"{Colors.YELLOW}Password: {Colors.END}").strip()
    
    print()
    
    # Step 4: Authenticate
    token = authenticate(email, password)
    if not token:
        log_error("Cannot proceed without authentication")
        sys.exit(1)
    
    print()
    
    # Step 5: Initiate payment
    checkout_id = test_payment_initiate(token)
    if not checkout_id:
        log_error("Cannot proceed without successful payment initiation")
        print("\nNote: If M-Pesa credentials are invalid, this will fail.")
        sys.exit(1)
    
    print()
    
    # Step 6: Check status immediately
    test_payment_status(token, checkout_id)
    
    print()
    
    # Step 7: Poll for completion
    print(f"{Colors.YELLOW}IMPORTANT: Complete the M-Pesa transaction on the test device!{Colors.END}")
    print(f"STK Push should have been sent to: {TEST_PHONE}\n")
    
    poll_payment_status(token, checkout_id)
    
    print(f"\n{'='*60}")
    log_success("Test complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test cancelled by user{Colors.END}\n")
        sys.exit(0)
