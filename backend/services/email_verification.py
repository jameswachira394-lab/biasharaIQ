import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging
import ssl

load_dotenv()

logger = logging.getLogger(__name__)

# Email Configuration
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "biasharaiq@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG_MODE = ENVIRONMENT == "development"
IS_PRODUCTION = ENVIRONMENT == "production"


def generate_verification_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def send_email(email: str, code: str) -> bool:
    """Send verification code via email.
    
    Production: Must have GMAIL_APP_PASSWORD configured
    Development: Falls back to console logging
    """
    
    msg = MIMEMultipart()
    msg["From"] = f"Biashara IQ <{GMAIL_ADDRESS}>"
    msg["To"] = email
    msg["Subject"] = "Verify Your Biashara IQ Account"

    body = f"""
Welcome to Biashara IQ!

Your verification code is: {code}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

---
Biashara IQ - Financial Intelligence for Kenyan SMEs
    """
    msg.attach(MIMEText(body, "plain"))

    # Production: MUST use SMTP
    if IS_PRODUCTION:
        if not GMAIL_APP_PASSWORD:
            logger.error("[EMAIL] ❌ PRODUCTION ERROR: GMAIL_APP_PASSWORD not configured in environment variables")
            logger.error(f"[EMAIL] Cannot send email to {email} in production without SMTP credentials")
            return False
        
        try:
            logger.info(f"[EMAIL] Attempting to send verification code to {email}")
            
            # Create secure connection
            context = ssl.create_default_context()
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls(context=context)
                server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"[EMAIL] ✅ Verification code sent successfully to {email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"[EMAIL] ❌ Authentication failed - Invalid GMAIL_APP_PASSWORD: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"[EMAIL] ❌ SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[EMAIL] ❌ Unexpected error sending email: {type(e).__name__}: {str(e)}")
            return False
    
    # Development mode: Log to console instead
    logger.warning(f"""
┌────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT MODE                        │
│                                                            │
│  Email NOT sent (SMTP disabled in development)            │
│  To: {email}
│  Code: {code}                                             │
│  Expires: In 10 minutes                                   │
│                                                            │
│  ✅ Use this code to verify the account                   │
└────────────────────────────────────────────────────────────┘
    """)
    return True