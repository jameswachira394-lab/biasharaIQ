import random
import string
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# In production, replace this with Redis or DB table
verification_store = {}

# Gmail Configuration
GMAIL_ADDRESS = "biasharaiq@gmail.com"
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")  # Use App Password, not regular Gmail password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def generate_verification_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def store_verification_code(email: str, code: str, expiry_minutes: int = 10):
    verification_store[email] = {
        "code": code,
        "expires_at": datetime.utcnow() + timedelta(minutes=expiry_minutes),
    }


def verify_code(email: str, code: str) -> bool:
    # Allow master code '123456' in development mode
    from core.config import settings
    if settings.DEBUG and code == "123456":
        print(f"[EMAIL SERVICE] [DEBUG] Bypassing verification with master code for {email}")
        return True

    record = verification_store.get(email)

    if not record:
        return False

    if datetime.utcnow() > record["expires_at"]:
        return False

    return record["code"] == code


def clear_verification_code(email: str):
    """Clear the verification code after successful verification"""
    if email in verification_store:
        del verification_store[email]


def send_email(email: str, code: str):
    """Send verification code via Gmail SMTP"""
    if not GMAIL_APP_PASSWORD:
        print(f"[EMAIL SERVICE] WARNING: GMAIL_APP_PASSWORD not set. Verification code for {email}: {code}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "BiasharaIQ Email Verification"
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = email

        # Plain text version
        text = f"""
Hello,

Your BiasharaIQ email verification code is:

{code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
The BiasharaIQ Team
        """

        # HTML version
        html = f"""
        <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif; color: #333; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #8B5E3C; margin: 0;">BiasharaIQ</h1>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">Financial Intelligence for Your Business</p>
                    </div>
                    
                    <div style="margin-bottom: 30px;">
                        <p style="font-size: 16px; margin-bottom: 20px;">Hello,</p>
                        <p style="font-size: 14px; color: #666; margin-bottom: 20px;">
                            Your <strong>BiasharaIQ email verification code</strong> is:
                        </p>
                        
                        <div style="background-color: #f9f9f9; border: 2px solid #8B5E3C; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0;">
                            <h2 style="letter-spacing: 5px; font-family: 'Courier New', monospace; color: #8B5E3C; margin: 0; font-size: 32px;">{code}</h2>
                        </div>
                        
                        <p style="font-size: 13px; color: #999; text-align: center; margin-bottom: 20px;">
                            This code will expire in <strong>10 minutes</strong>
                        </p>
                        
                        <p style="font-size: 14px; color: #666; margin-bottom: 10px;">
                            If you didn't request this code, please ignore this email.
                        </p>
                    </div>
                    
                    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; font-size: 12px; color: #999;">
                        <p style="margin: 5px 0;">© 2026 BiasharaIQ. All rights reserved.</p>
                        <p style="margin: 5px 0;">Financial intelligence for Kenyan businesses 🇰🇪</p>
                    </div>
                </div>
            </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        msg.attach(part1)
        msg.attach(part2)

        # Send email via Gmail SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL SERVICE] [SUCCESS] Verification code sent to {email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print(f"[EMAIL SERVICE] [FAIL] Authentication failed. Check GMAIL_APP_PASSWORD in .env")
        print(f"[FALLBACK] Verification code for {email}: {code}")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL SERVICE] [FAIL] SMTP error: {str(e)}")
        print(f"[FALLBACK] Verification code for {email}: {code}")
        return False
    except Exception as e:
        print(f"[EMAIL SERVICE] [ERROR] Error sending email: {str(e)}")
        print(f"[FALLBACK] Verification code for {email}: {code}")
        return False

