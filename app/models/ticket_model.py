from app.db.db import Base
from sqlalchemy import Column, Integer, String
from pydantic import  BaseModel, Field
class Ticket_model(BaseModel):
    title: str = Field(min_length=5,max_length=50)
    description: str = Field(min_length=15, max_length=200)
    category: str = Field(min_length=4, max_length=10)
    file: str | None = Field(default=None)


class Ticket(Base):
    __tablename__ = "Ticket"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    description = Column(String, nullable=False)
    category = Column(String,nullable=False)
    file = Column(String, nullable=True)