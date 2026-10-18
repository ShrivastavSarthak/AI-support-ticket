
import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

from app.models.email_model import Email_model

load_dotenv()


def email_service(mail: Email_model):
    print("mail",mail)
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_email = os.getenv("SMTP_EMAIL")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not all([smtp_host, smtp_email, smtp_password]):
            raise ValueError("Missing SMTP configuration in .env")

        message = EmailMessage()
        message["From"] = smtp_email
        message["To"] = mail.receiver_mail
        message["Subject"] = mail.title

        # HTML email content
        message.set_content(mail.content, subtype="html")

        # Connect and send
        context = ssl.create_default_context()

        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_email, smtp_password)
            server.send_message(message)

        return {
            "success": True,
            "message": f"Email sent to {mail.receiver_mail}",
        }

    except Exception as e:
        print(f"Error sending email: {type(e).__name__}: {e}")
        return {
            "success": False,
            "message": f"Error sending email: {str(e)}",
        }
