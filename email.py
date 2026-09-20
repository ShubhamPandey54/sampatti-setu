"""
Sends real emails over SMTP. Works with Gmail out of the box:

1. Turn on 2-Step Verification on the Gmail account:
   https://myaccount.google.com/security
2. Create an "App Password": https://myaccount.google.com/apppasswords
   (choose "Mail" as the app) — Google gives you a 16-character code.
3. Put that code (not your normal Gmail password) into .env as SMTP_PASSWORD.

Any other SMTP provider (Outlook, SendGrid's SMTP relay, your college/office
mail server) works too — just change SMTP_HOST/PORT in .env.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_email(to_email: str, subject: str, body_text: str) -> None:
    msg = MIMEMultipart()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_from, [to_email], msg.as_string())


def send_otp_email(to_email: str, otp_code: str) -> None:
    send_email(
        to_email=to_email,
        subject="Your SAMPATTI-SETU verification code",
        body_text=(
            f"Your verification code is: {otp_code}\n\n"
            "This code expires in 10 minutes. If you did not request this, "
            "you can ignore this email.\n\n"
            "— Sampatti-Setu, Delhi Police"
        ),
    )
