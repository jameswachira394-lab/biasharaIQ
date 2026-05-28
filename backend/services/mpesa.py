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
        
        # B2B settings
        self.b2b_initiator = settings.MPESA_B2B_INITIATOR
        self.b2b_security_credential = settings.MPESA_B2B_SECURITY_CREDENTIAL
        self.b2b_initiator_password = settings.MPESA_B2B_INITIATOR_PASSWORD
        self.b2b_cert_path = settings.MPESA_B2B_CERT_PATH
        
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

        # Format phone: 2547XXXXXXXX
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]

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
                "checkout_id": stk_callback.get("CheckoutRequestID")
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
            "date": metadata.get("TransactionDate")
        }

    def encrypt_b2b_security_credential(self, password: str, cert_path: str) -> Optional[str]:
        """Encrypt plain-text initiator password using Safaricom's public certificate."""
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives.asymmetric import padding
            
            with open(cert_path, "rb") as cert_file:
                cert_data = cert_file.read()
                
            # Try loading as PEM first, then DER
            try:
                cert = x509.load_pem_x509_certificate(cert_data)
            except ValueError:
                cert = x509.load_der_x509_certificate(cert_data)
                
            public_key = cert.public_key()
            
            # Safaricom requires PKCS#1 v1.5 padding
            encrypted = public_key.encrypt(
                password.encode("utf-8"),
                padding.PKCS1v15()
            )
            return base64.b64encode(encrypted).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encrypt security credential with certificate at {cert_path}: {str(e)}")
            return None

    def initiate_b2b_payment_request(
        self,
        sender_shortcode: str,
        amount: int,
        account_ref: str,
        remarks: str = "Subscription Payment",
        initiator: Optional[str] = None,
        security_credential: Optional[str] = None,
        receiver_shortcode: Optional[str] = None,
        command_id: str = "BusinessPayBill"
    ) -> Dict[str, Any]:
        """Initiate B2B Payment Request (Business PayBill or Buy Goods)."""
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Failed to authenticate with M-Pesa. Check your credentials in .env", "status": 500}

        # Resolve PartyB (Receiver Shortcode) - defaults to our configured shortcode
        party_b = receiver_shortcode or self.shortcode
        if not party_b:
            return {"error": "Receiver shortcode (PartyB) is not configured.", "status": 500}

        # Resolve Initiator
        api_initiator = initiator or self.b2b_initiator or "testapi"

        # Resolve SecurityCredential
        api_security_credential = security_credential or self.b2b_security_credential
        if not api_security_credential:
            # If plain text password and cert path are provided, encrypt dynamically
            if self.b2b_initiator_password and self.b2b_cert_path:
                import os
                if os.path.exists(self.b2b_cert_path):
                    api_security_credential = self.encrypt_b2b_security_credential(
                        self.b2b_initiator_password, self.b2b_cert_path
                    )
            
            # If still not resolved and in sandbox, fallback to a mock/placeholder
            if not api_security_credential:
                if self.environment == "sandbox":
                    logger.warning("No B2B SecurityCredential configured or generated; using placeholder.")
                    api_security_credential = "simulated-credential"
                else:
                    return {"error": "M-Pesa B2B SecurityCredential or certificate not configured.", "status": 500}

        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Prepare B2B payload
        payload = {
            "Initiator": api_initiator,
            "SecurityCredential": api_security_credential,
            "CommandID": command_id,
            "SenderIdentifierType": "4",
            "RecieverIdentifierType": "4",
            "Amount": str(amount),
            "PartyA": sender_shortcode,
            "PartyB": party_b,
            "AccountReference": account_ref,
            "Remarks": remarks[:100],  # Max 100 chars
            "QueueTimeOutURL": self.callback_url,
            "ResultURL": self.callback_url.replace("/callback", "/b2b-callback") if "/callback" in self.callback_url else f"{self.callback_url}/b2b"
        }

        try:
            api_url = f"{self.base_url}/mpesa/b2b/v1/paymentrequest"
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            
            logger.debug(f"M-Pesa B2B Response: {response.status_code} - {response.text}")
            data = response.json()
            
            if response.status_code != 200:
                error_msg = data.get("errorMessage", data.get("error", "Unknown error from M-Pesa B2B API"))
                logger.error(f"M-Pesa B2B API Error: {error_msg}")
                return {"error": f"M-Pesa B2B API Error: {error_msg}", "status": response.status_code}
            
            return data
            
        except requests.exceptions.Timeout:
            error_msg = "Request to M-Pesa B2B API timed out."
            logger.error(f"B2B Payment timeout: {error_msg}")
            return {"error": error_msg, "status": 500}
        except Exception as e:
            error_msg = f"Unexpected error during B2B Payment: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg, "status": 500}

    def verify_b2b_callback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and verify M-Pesa B2B callback data."""
        result = data.get("Result", {})
        result_code = result.get("ResultCode")
        
        if result_code != 0:
            return {
                "success": False,
                "message": result.get("ResultDesc", "Transaction failed"),
                "checkout_id": result.get("ConversationID"),
                "merchant_id": result.get("OriginatorConversationID")
            }

        # Parse ResultParameters
        result_parameters = result.get("ResultParameters", {}).get("ResultParameter", [])
        metadata = {}
        for item in result_parameters:
            metadata[item.get("Key")] = item.get("Value")

        # The receipt can be TransactionReceipt or TransactionID directly
        receipt = metadata.get("TransactionReceipt") or result.get("TransactionID")
        amount = metadata.get("TransactionAmount")

        return {
            "success": True,
            "checkout_id": result.get("ConversationID"),
            "merchant_id": result.get("OriginatorConversationID"),
            "receipt": receipt,
            "amount": amount,
            "date": metadata.get("TransactionCompletedDateTime")
        }
