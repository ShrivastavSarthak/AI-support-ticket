from app.models.email_model import Email_model
import resend
from dotenv import load_dotenv
import os
load_dotenv()

def email_service(mail:Email_model):
    r = resend.Emails.send({
        "from": os.getenv("SENDER_EMAIL"),
        "to": mail.receiver_mail,
        "subject": mail.title,
        "html": mail.content
    })
    
    return r