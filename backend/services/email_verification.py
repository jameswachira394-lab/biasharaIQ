import secrets
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
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
IS_PRODUCTION = ENVIRONMENT == "production"


def generate_verification_code(length: int = 6) -> str:
    """Generate a cryptographically secure numeric verification code."""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def _send_via_smtp(msg: MIMEMultipart, recipient: str) -> bool:
    """Attempt SMTP delivery. Returns True on success, False on any failure."""
    if not GMAIL_APP_PASSWORD:
        logger.error(
            "[EMAIL] PRODUCTION ERROR: GMAIL_APP_PASSWORD not set — "
            "cannot send to %s", recipient
        )
        return False

    try:
        logger.info("[EMAIL] Sending verification email to %s via SMTP", recipient)
        logger.info("[EMAIL] Using Gmail address: %s", GMAIL_ADDRESS)
        context = ssl.create_default_context()

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            logger.info("[EMAIL] Connected to SMTP server: %s:%s", SMTP_SERVER, SMTP_PORT)
            server.starttls(context=context)
            logger.info("[EMAIL] TLS connection established")
            # Remove spaces from app password
            clean_password = GMAIL_APP_PASSWORD.replace(" ", "")
            server.login(GMAIL_ADDRESS, clean_password)
            logger.info("[EMAIL] Successfully authenticated")
            server.send_message(msg)

        logger.info("[EMAIL] ✓ Verification email delivered to %s", recipient)
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error("[EMAIL] ✗ SMTP Authentication failed: %s — ensure Gmail 2FA is enabled and app password is correct", e)
    except smtplib.SMTPException as e:
        logger.error("[EMAIL] ✗ SMTP error sending to %s: %s", recipient, e)
    except Exception as e:
        logger.error("[EMAIL] ✗ Unexpected error sending to %s: %s: %s", recipient, type(e).__name__, e)

    return False


def send_email(email: str, code: str) -> bool:
    """Send a verification code email.

    Production: requires GMAIL_APP_PASSWORD in environment.
    Development: logs the code to console and returns True.
    """
    msg = MIMEMultipart()
    msg["From"] = f"Biashara IQ <{GMAIL_ADDRESS}>"
    msg["To"] = email
    msg["Subject"] = "Verify Your Biashara IQ Account"

    body = (
        "Welcome to Biashara IQ!\n\n"
        f"Your verification code is: {code}\n\n"
        "This code will expire in 10 minutes.\n\n"
        "If you did not request this code, please ignore this email.\n\n"
        "---\n"
        "Biashara IQ - Financial Intelligence for Kenyan SMEs\n"
    )
    msg.attach(MIMEText(body, "plain"))

    if IS_PRODUCTION:
        return _send_via_smtp(msg, email)

    # Development fallback — never log the code in production
    logger.warning(
        "[EMAIL] Development mode — SMTP skipped.\n"
        "  Recipient : %s\n"
        "  Code      : %s\n"
        "  Expires   : 10 minutes",
        email, code,
    )
    return True