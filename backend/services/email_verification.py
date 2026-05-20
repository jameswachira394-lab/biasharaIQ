import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Gmail Configuration
GMAIL_ADDRESS = "biasharaiq@gmail.com"
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # Use App Password, not regular Gmail password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def generate_verification_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def send_email(email: str, code: str):
    """Send verification code via Gmail SMTP"""
    if not GMAIL_APP_PASSWORD:
        print(f"[EMAIL SERVICE] WARNING: GMAIL_APP_PASSWORD not set. Verification code for {email}: {code}")
        return False

    msg = MIMEMultipart()
    msg["From"] = f"Biashara IQ <{GMAIL_ADDRESS}>"
    msg["To"] = email
    msg["Subject"] = "Verify Your Biashara IQ Account"

    body = f"""
    Welcome to Biashara IQ!

    Your verification code is: {code}

    This code will expire in 10 minutes.

    If you did not request this code, please ignore this email.
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL SERVICE] [SUCCESS] Verification code sent to {email}")
        return True
    except smtplib.SMTPException as e:
        print(f"[EMAIL SERVICE] [FAIL] SMTP error: {str(e)}")
        print(f"[FALLBACK] Verification code for {email}: {code}")
        return False
    except Exception as e:
        print(f"[EMAIL SERVICE] [ERROR] Error sending email: {str(e)}")
        print(f"[FALLBACK] Verification code for {email}: {code}")
        return False