from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = config("DB_URL")

if not DB_URL:
    DB_URL = "sqlite:///./app.db"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
