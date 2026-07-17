import base64
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class MpesaService:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        self.environment = settings.MPESA_ENVIRONMENT

        
        if self.environment == "production":
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"
        
        # Validate configuration on initialization
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate that all required M-Pesa configuration is present."""
        missing_config = []
        
        if not self.consumer_key:
            missing_config.append("MPESA_CONSUMER_KEY")
        if not self.consumer_secret:
            missing_config.append("MPESA_CONSUMER_SECRET")
        if not self.shortcode:
            missing_config.append("MPESA_SHORTCODE")
        if not self.passkey:
            missing_config.append("MPESA_PASSKEY")
        if not self.callback_url:
            missing_config.append("MPESA_CALLBACK_URL")
        
        if missing_config:
            error_msg = f"Missing M-Pesa configuration: {', '.join(missing_config)}. Please check your .env file."
            logger.error(error_msg)
            # Don't raise exception here - let it fail gracefully during payment attempt

    def get_access_token(self) -> Optional[str]:
        """Get OAuth access token from Safaricom."""
        # Check credentials first
        if not self.consumer_key or not self.consumer_secret:
            logger.error("M-Pesa credentials not configured. Set MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET in .env")
            return None
            
        try:
            api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            response = requests.get(
                api_url, 
                auth=(self.consumer_key, self.consumer_secret),
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.Timeout:
            logger.error("M-Pesa authentication request timed out (network issue or API slow)")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("M-Pesa authentication failed: Invalid credentials (check MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET)")
            else:
                logger.error(f"M-Pesa authentication failed with status {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting M-Pesa access token: {str(e)}")
            return None

    def initiate_stk_push(self, phone: str, amount: int, account_ref: str) -> Dict[str, Any]:
        """Initiate M-Pesa STK Push (Lipa na M-Pesa Online)."""
        # Validate callback URL
        if not self.callback_url:
            return {"error": "M-Pesa callback URL not configured. Set MPESA_CALLBACK_URL in .env", "status": 500}
            
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to authenticate with M-Pesa. Check your credentials in .env", "status": 500}

        # Robustly format phone to Safaricom standard 254XXXXXXXXX
        cleaned_phone = "".join(c for c in phone if c.isdigit())
        if cleaned_phone.startswith('0') and len(cleaned_phone) == 10:
            phone = '254' + cleaned_phone[1:]
        elif cleaned_phone.startswith('254') and len(cleaned_phone) == 12:
            phone = cleaned_phone
        else:
            phone = cleaned_phone

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{self.shortcode}{self.passkey}{timestamp}".encode()
        ).decode('utf-8')

        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": account_ref,
            "TransactionDesc": f"Payment for {account_ref}"
        }

        try:
            api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            
            # Log the response for debugging
            logger.debug(f"M-Pesa API Response: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Check if API returned an error
            if response.status_code != 200:
                error_msg = data.get("errorMessage", data.get("error", "Unknown error from M-Pesa API"))
                logger.error(f"M-Pesa API Error: {error_msg}")
                return {"error": f"M-Pesa API Error: {error_msg}", "status": response.status_code}
            
            return data
            
        except requests.exceptions.Timeout:
            error_msg = "Request to M-Pesa API timed out. Please try again."
            logger.error(f"STK Push timeout: {error_msg}")
            return {"error": error_msg, "status": 500}
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to M-Pesa API. Check your network connection."
            logger.error(f"STK Push connection error: {error_msg}")
            return {"error": error_msg, "status": 500}
        except Exception as e:
            error_msg = f"Unexpected error during STK Push: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "status": 500}

    def verify_callback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and verify M-Pesa callback data."""
        stk_callback = data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        
        if result_code != 0:
            return {
                "success": False,
                "message": stk_callback.get("ResultDesc", "Transaction failed"),
                "checkout_id": stk_callback.get("CheckoutRequestID"),
                "result_code": result_code
            }

        # Parse metadata
        callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        metadata = {}
        for item in callback_metadata:
            metadata[item.get("Name")] = item.get("Value")

        return {
            "success": True,
            "checkout_id": stk_callback.get("CheckoutRequestID"),
            "merchant_id": stk_callback.get("MerchantRequestID"),
            "receipt": metadata.get("MpesaReceiptNumber"),
            "amount": metadata.get("Amount"),
            "phone": metadata.get("PhoneNumber"),
            "date": metadata.get("TransactionDate"),
            "result_code": result_code
        }

