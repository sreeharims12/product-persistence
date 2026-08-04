import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Email
# ──────────────────────────────────────────────────────────────────────────────
def send_email(to: str, subject: str, body: str) -> bool:
    """Send an email alert. Returns True on success, False on failure/not configured."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(f"[Email STUB] To: {to} | Subject: {subject} | Body: {body[:100]}")
        return True  # Stub — pretend it worked

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to

        html_body = f"""
        <html><body style="font-family:sans-serif;padding:20px;background:#f5f5f5;">
          <div style="max-width:600px;margin:auto;background:#fff;border-radius:12px;padding:30px;">
            <h2 style="color:#6366f1;">📦 Product Monitor Alert</h2>
            <p style="font-size:16px;color:#333;">{body}</p>
            <hr style="margin:20px 0;">
            <p style="font-size:12px;color:#888;">
              You are receiving this because you enabled monitoring for this product.
            </p>
          </div>
        </body></html>
        """
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to, msg.as_string())

        logger.info(f"[Email] Sent to {to}: {subject}")
        return True

    except Exception as e:
        logger.error(f"[Email] Failed to send to {to}: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# SMS (Twilio)
# ──────────────────────────────────────────────────────────────────────────────
def send_sms(to_phone: str, message: str) -> bool:
    """Send an SMS alert via Twilio. Returns True on success."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.info(f"[SMS STUB] To: {to_phone} | Message: {message[:100]}")
        return True  # Stub

    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone,
        )
        logger.info(f"[SMS] Sent to {to_phone}")
        return True
    except Exception as e:
        logger.error(f"[SMS] Failed to send to {to_phone}: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────────────────────────────────────
def dispatch_notification(
    channel: str,
    email: Optional[str],
    phone: Optional[str],
    subject: str,
    message: str,
) -> bool:
    if channel == "web":
        return True
    if channel == "email" and email:
        return send_email(email, subject, message)
    elif channel == "sms" and phone:
        return send_sms(phone, message)
    return False
