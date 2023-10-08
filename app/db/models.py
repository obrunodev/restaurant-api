from app.db.base import Base
from sqlalchemy import Column, Integer, String, Float


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Integer)


class OrderHistory(Base):
    __tablename__ = "orders_history"

    id = Column(Integer, primary_key=True, index=True)
    table = Column(Integer, index=True)
    products = Column(String, index=True)
