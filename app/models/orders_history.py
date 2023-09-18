from app.db import engine

from pydantic import BaseModel

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class OrderHistory(Base):
    __tablename__ = "orders_history"

    id = Column(Integer, primary_key=True, index=True)
    table = Column(Integer, index=True)
    products = Column(String, index=True)

class OrderHistoryCreate(BaseModel):
    table: int
    products: str

class OrderHistoryOut(BaseModel):
    id: int
    table: int
    products: str

Base.metadata.create_all(bind=engine)
