import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# SMTP Config
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "user@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-smtp-password")

def _send_real_email(to_email: str, subject: str, body: str):
    """Internal helper for real SMTP sending"""
    if "example.com" in SMTP_SERVER or not SMTP_PASSWORD:
        logger.info(f"--- MOCK EMAIL (No SMTP Config) ---")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body snippet: {body[:50]}...")
        logger.info(f"------------------------------------")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_verification_email(email: str, otp: str):
    subject = "Verify your email address"
    body = f"Welcome! Your verification code is: {otp}\n\nThis code will expire in 10 minutes."
    _send_real_email(email, subject, body)

def send_password_reset_email(email: str, token: str):
    subject = "Password Reset Request"
    body = f"Reset your password using this token: {token}"
    _send_real_email(email, subject, body)
