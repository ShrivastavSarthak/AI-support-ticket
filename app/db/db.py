import os 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("--->",db_url)
    raise ValueError("Database URL is missing")
    
engine = create_engine(db_url)
session = sessionmaker(autoflush=False,bind=engine, autocommit = False)
Base =declarative_base()

def CallDB():
    db= session()
    try:
        yield db
    finally:
        db.close()