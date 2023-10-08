from app.db.connection import Session
from app.db.models import Product
from app.schemas.products import ProductOut

from pydantic import BaseModel, validator

from typing import List


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
        db = Session()
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
