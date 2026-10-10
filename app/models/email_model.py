from pydantic import BaseModel, EmailStr, Field

class Email_model(BaseModel):
    receiver_mail: EmailStr
    content: str = Field(min_length=100, max_length=500)
    title: str = Field(min_length=5, max_length=15)