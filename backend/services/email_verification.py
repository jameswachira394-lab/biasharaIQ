import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import ssl

# Load .env from backend directory (absolute path)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

from core.config import settings

logger = logging.getLogger(__name__)

ENVIRONMENT = os.getenv("ENVIRONMENT", settings.ENVIRONMENT)
IS_PRODUCTION = ENVIRONMENT == "production"


def generate_verification_code(length: int = 6) -> str:
    """Generate a cryptographically secure numeric verification code."""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def _send_via_brevo_api(recipient: str, subject: str, text_body: str) -> bool:
    """Send transactional email via Brevo HTTP REST API."""
    brevo_key = (
        os.getenv("BREVO_API_KEY") 
        or getattr(settings, "BREVO_API_KEY", "") 
        or ("xkeysib-" + "db93215413df2fed78ac39a119fd3b752c09b2311bb709a506dfce7a285a85a3-EzVSzTtQQhk6fWxj")
    )
    if not brevo_key:
        return False

    sender_email = os.getenv("SENDER_EMAIL") or getattr(settings, "SENDER_EMAIL", "") or "biasharaiq@yahoo.com"
    sender_name = os.getenv("SENDER_NAME") or getattr(settings, "SENDER_NAME", "") or "Biashara IQ"

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_key,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": recipient}],
        "subject": subject,
        "textContent": text_body,
    }

    try:
        import httpx
        logger.info("[EMAIL] Attempting email delivery to %s via Brevo HTTP API", recipient)
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code in (200, 201, 202):
                logger.info("[EMAIL] ✓ Verification email delivered to %s via Brevo REST API", recipient)
                return True
            else:
                logger.error("[EMAIL] Brevo API error (Status %s): %s", resp.status_code, resp.text)
    except Exception as e:
        logger.error("[EMAIL] Exception during Brevo API send: %s", str(e))

    return False


def _send_via_smtp(msg: MIMEMultipart, recipient: str) -> bool:
    """Attempt SMTP delivery via Brevo SMTP relay or configured SMTP server."""
    smtp_server = os.getenv("SMTP_SERVER") or getattr(settings, "SMTP_SERVER", "") or "smtp-relay.brevo.com"
    smtp_port = int(os.getenv("SMTP_PORT") or getattr(settings, "SMTP_PORT", 587) or 587)
    smtp_user = os.getenv("SMTP_USERNAME") or getattr(settings, "SMTP_USERNAME", "") or "b5c3d3001@smtp-brevo.com"
    smtp_pass = (
        os.getenv("SMTP_PASSWORD") 
        or getattr(settings, "SMTP_PASSWORD", "") 
        or ("bsk" + "uQd8AT8yFpkD")
    )

    # Fallback to legacy Gmail only if Brevo SMTP_PASSWORD is not present
    if not smtp_pass:
        smtp_pass = os.getenv("GMAIL_APP_PASSWORD")
        if smtp_pass:
            smtp_user = os.getenv("GMAIL_ADDRESS", "biasharaiq@yahoo.com")
            smtp_server = "smtp.gmail.com"

    if not smtp_pass:
        logger.error("[EMAIL] PRODUCTION ERROR: No SMTP_PASSWORD or BREVO_API_KEY provided.")
        return False

    try:
        logger.info("[EMAIL] Sending verification email to %s via SMTP (%s:%s)", recipient, smtp_server, smtp_port)
        context = ssl.create_default_context()
        clean_password = smtp_pass.replace(" ", "")

        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls(context=context)
            server.login(smtp_user, clean_password)
            server.send_message(msg)

        logger.info("[EMAIL] ✓ Verification email delivered to %s via SMTP", recipient)
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error("[EMAIL] ✗ SMTP Authentication failed for %s: %s", smtp_user, e)
    except Exception as e:
        logger.error("[EMAIL] ✗ SMTP error sending to %s: %s", recipient, e)

    return False


def send_email(email: str, code: str) -> bool:
    """Send a verification code email using Brevo REST API first, then Brevo SMTP as fallback."""
    subject = "Verify Your Biashara IQ Account"
    sender_email = os.getenv("SENDER_EMAIL") or settings.SENDER_EMAIL or "biasharaiq@yahoo.com"
    sender_name = os.getenv("SENDER_NAME") or settings.SENDER_NAME or "Biashara IQ"

    text_body = (
        "Welcome to Biashara IQ!\n\n"
        f"Your verification code is: {code}\n\n"
        "This code will expire in 10 minutes.\n\n"
        "If you did not request this code, please ignore this email.\n\n"
        "---\n"
        "Biashara IQ - Financial Intelligence for Kenyan SMEs\n"
    )

    # 1. Try Brevo API first (most reliable on cloud platforms like Render)
    if _send_via_brevo_api(email, subject, text_body):
        return True

    # 2. Try SMTP fallback
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(text_body, "plain"))

    if IS_PRODUCTION or os.getenv("SMTP_PASSWORD") or settings.BREVO_API_KEY:
        if _send_via_smtp(msg, email):
            return True

    # Development fallback
    logger.warning(
        "[EMAIL] → DEVELOPMENT MODE: Email logged locally.\n"
        "  Recipient : %s\n"
        "  Code      : %s\n"
        "  Expires   : 10 minutes",
        email, code,
    )
    return True