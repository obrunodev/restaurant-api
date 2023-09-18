from app.db import SessionLocal, engine
from app.models.products import Product, ProductOut

from pydantic import BaseModel, validator

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer

from typing import List

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Integer)

class OrderCreate(BaseModel):
    table: int
    product_id: int
    quantity: int

    @validator("table")
    def table_must_be_positive(cls, value):
        if value < 1:
            raise ValueError("Mesa deve ser maior que zero")
        return value
    
    @validator("quantity")
    def quantity_must_be_positive(cls, value):
        if value < 1:
            raise ValueError("Quantidade deve ser maior que zero")
        return value
    
    @validator("product_id")
    def product_id_must_exist(cls, value):
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == value).first()
        db.close()
        if product is None:
            raise ValueError("Produto não encontrado")
        return value

class OrderOut(BaseModel):
    id: int
    table: int
    product: ProductOut
    quantity: int

class OrderResponse(BaseModel):
    orders: List[OrderOut]
    total_price: float

Base.metadata.create_all(bind=engine)
