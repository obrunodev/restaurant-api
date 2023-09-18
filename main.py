from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crie uma classe de modelo usando SQLAlchemy
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

# Modelo de comanda para pedidos de restaurante
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Integer)

# Crie a tabela no banco de dados (execute isso uma vez para criar a tabela)
Base.metadata.create_all(bind=engine)

# Modelo de dados Pydantic para entrada de pedido
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
    
    # def model_dump(self):
    #     return {
    #         "table": self.table,
    #         "product_id": self.product_id,
    #         "quantity": self.quantity
    #     }

# Modelo de dados Pydantic para saída de pedido
class OrderOut(BaseModel):
    id: int
    table: int
    product_id: int
    quantity: int

# Rota para criar um pedido
@app.post("/orders/", response_model=OrderOut)
def create_order(order: OrderCreate):
    db = SessionLocal()
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    db.close()
    return db_order

# Rota para listar todos os pedidos
@app.get("/orders/", response_model=list[OrderOut])
def get_all_orders():
    db = SessionLocal()
    orders = db.query(Order).all()
    db.close()
    return orders

# Rota para listar um pedido específico
@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int):
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    db.close()
    if order is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order

# Rota para atualizar um pedido
@app.put("/orders/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order: OrderCreate):
    db = SessionLocal()
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    db_order.table = order.table
    db_order.product_id = order.product_id
    db_order.quantity = order.quantity
    db.commit()
    db.refresh(db_order)
    db.close()
    return db_order

# Rota para remover um pedido
@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    db = SessionLocal()
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    db.delete(db_order)
    db.commit()
    db.close()
    return {"message": "Pedido removido com sucesso"}

# Modelo de dados Pydantic para entrada de produto
class ProductCreate(BaseModel):
    name: str
    price: float

# Modelo de dados Pydantic para saída de produto
class ProductOut(BaseModel):
    id: int
    name: str
    price: float

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

@app.post("/products/", response_model=ProductOut)
def create_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.get("/products/", response_model=list[ProductOut])
def get_all_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductCreate):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db_product.name = product.name
    db_product.price = product.price
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(db_product)
    db.commit()
    db.close()
    return {"message": "Produto removido com sucesso"}
