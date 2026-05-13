#!/usr/bin/env python3
"""
M-Pesa Credentials Validator
Test M-Pesa credentials without running the full backend
"""

import os
import sys
import requests
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'


def log_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def log_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def log_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def log_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def log_header(msg):
    print(f"\n{Colors.CYAN}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{Colors.END}\n")


def load_env():
    """Load .env file"""
    backend_dir = Path(__file__).parent / "backend"
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        log_error(f".env file not found at {env_file}")
        log_info("Create it with: python setup_mpesa.py")
        return False
    
    load_dotenv(str(env_file))
    log_success(f".env loaded from {env_file}")
    return True


def check_configuration():
    """Check if all required M-Pesa configuration is present"""
    log_header("Checking M-Pesa Configuration")
    
    config = {
        "MPESA_CONSUMER_KEY": os.getenv("MPESA_CONSUMER_KEY", "").strip(),
        "MPESA_CONSUMER_SECRET": os.getenv("MPESA_CONSUMER_SECRET", "").strip(),
        "MPESA_SHORTCODE": os.getenv("MPESA_SHORTCODE", "").strip(),
        "MPESA_PASSKEY": os.getenv("MPESA_PASSKEY", "").strip(),
        "MPESA_CALLBACK_URL": os.getenv("MPESA_CALLBACK_URL", "").strip(),
        "MPESA_ENVIRONMENT": os.getenv("MPESA_ENVIRONMENT", "sandbox").strip(),
    }
    
    all_present = True
    
    for key, value in config.items():
        if key == "MPESA_CONSUMER_SECRET" or key == "MPESA_PASSKEY":
            display = f"{'*' * 20}..." if value else "(empty)"
        else:
            display = value or "(empty)"
        
        if not value:
            log_error(f"{key}: {display}")
            all_present = False
        else:
            log_success(f"{key}: {display}")
    
    return config if all_present else None


def test_credentials(config):
    """Test M-Pesa credentials"""
    log_header("Testing M-Pesa Credentials")
    
    environment = config["MPESA_ENVIRONMENT"]
    base_url = "https://sandbox.safaricom.co.ke" if environment == "sandbox" else "https://api.safaricom.co.ke"
    
    log_info(f"Environment: {environment}")
    log_info(f"API URL: {base_url}")
    
    # Test OAuth token
    log_info("Testing OAuth authentication...")
    
    try:
        api_url = f"{base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(
            api_url,
            auth=(config["MPESA_CONSUMER_KEY"], config["MPESA_CONSUMER_SECRET"]),
            timeout=10
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                log_success(f"OAuth authentication successful")
                log_info(f"Token: {token[:50]}...")
                return token
            else:
                log_error("No access token in response")
                log_info(f"Response: {response.json()}")
                return None
        else:
            log_error(f"OAuth failed with status {response.status_code}")
            log_info(f"Response: {response.text}")
            
            if response.status_code == 401:
                log_error("Invalid credentials - Check MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET")
            return None
            
    except requests.exceptions.Timeout:
        log_error("Request timed out - M-Pesa API may be slow or unreachable")
        return None
    except requests.exceptions.ConnectionError:
        log_error("Connection error - Cannot reach M-Pesa API")
        log_info("Check your internet connection")
        return None
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        return None


def test_stk_push_format(config):
    """Test STK Push request format (without sending)"""
    log_header("Validating STK Push Request Format")
    
    # Test phone formatting
    test_phones = ["0708374149", "254708374149", "+254708374149"]
    
    for phone in test_phones:
        # Format phone: 2547XXXXXXXX
        if phone.startswith('0'):
            formatted = '254' + phone[1:]
        elif phone.startswith('+'):
            formatted = phone[1:]
        else:
            formatted = phone
        
        log_success(f"Phone formatting: {phone} → {formatted}")
    
    # Test password generation
    shortcode = config["MPESA_SHORTCODE"]
    passkey = config["MPESA_PASSKEY"]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    password_string = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(password_string.encode()).decode('utf-8')
    
    log_info(f"Shortcode: {shortcode}")
    log_info(f"Timestamp: {timestamp}")
    log_success(f"Generated password (base64): {password[:30]}...")
    
    # Test payload structure
    log_info("\nSTK Push payload structure (test):")
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 100,
        "PartyA": "254708374149",
        "PartyB": shortcode,
        "PhoneNumber": "254708374149",
        "CallBackURL": config["MPESA_CALLBACK_URL"],
        "AccountReference": "TestRef",
        "TransactionDesc": "Test Payment"
    }
    
    import json
    log_info(json.dumps(payload, indent=2))
    
    # Validate callback URL
    log_header("Validating Callback URL")
    
    callback_url = config["MPESA_CALLBACK_URL"]
    if not callback_url:
        log_error("MPESA_CALLBACK_URL is not set")
    elif not callback_url.startswith("http"):
        log_error(f"Invalid callback URL: {callback_url} (must start with http:// or https://)")
    elif environment == "production" and not callback_url.startswith("https"):
        log_warning(f"Callback URL is not HTTPS (required for production): {callback_url}")
    else:
        log_success(f"Callback URL: {callback_url}")


def suggest_next_steps():
    """Suggest next steps"""
    log_header("Next Steps")
    
    print("""
1. Start your backend server:
   cd backend
   python main.py

2. Run the integration test:
   python test_mpesa_integration.py

3. If tests pass, try a payment from the frontend:
   - Go to https://biashara-iq.vercel.app (or your frontend)
   - Navigate to Pricing page
   - Click "Upgrade to Pro"
   - Follow M-Pesa prompt

4. Monitor backend logs:
   Look for messages like:
   - "Initiating payment..."
   - "STK Push initiated"
   - "M-Pesa callback received"

5. Troubleshooting:
   - Check backend logs for exact error messages
   - Verify M-Pesa credentials are correct at:
     https://developer.safaricom.co.ke/
   - Test with small amounts (1 KES minimum)
   - In sandbox, check M-Pesa test account:
     https://sandbox.safaricom.co.ke/
""")


def main():
    log_header("M-Pesa Credentials Validator")
    
    # Load environment
    if not load_env():
        log_error("Cannot proceed without .env file")
        sys.exit(1)
    
    # Check configuration
    config = check_configuration()
    if not config:
        log_error("Missing required M-Pesa configuration")
        log_info("Run: python setup_mpesa.py")
        sys.exit(1)
    
    # Test credentials
    token = test_credentials(config)
    if not token:
        log_error("Credential test failed")
        log_info("Check your M-Pesa credentials at https://developer.safaricom.co.ke/")
        sys.exit(1)
    
    # Validate STK Push format
    test_stk_push_format(config)
    
    # Suggest next steps
    suggest_next_steps()
    
    log_header("Validation Complete!")
    log_success("M-Pesa credentials appear to be valid")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user")
        sys.exit(0)
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
