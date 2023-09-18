from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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

# Crie a tabela no banco de dados (execute isso uma vez para criar a tabela)
Base.metadata.create_all(bind=engine)

class ProductCreate(BaseModel):
    name: str
    price: float

class ProductOut(BaseModel):
    id: int
    name: str
    price: float

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

class OrderHistoryCreate(BaseModel):
    table: int
    products: str

class OrderHistoryOut(BaseModel):
    id: int
    table: int
    products: str

@app.post("/orders/", response_model=OrderOut)
def create_order(order: OrderCreate):
    db = SessionLocal()

    product = db.query(Product).get(order.product_id)
    if product is None:
        db.close()
        raise HTTPException(status_code=400, detail="Produto não encontrado")
    
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    product_out = ProductOut(
        id=product.id,
        name=product.name,
        price=product.price
    )

    order_out = OrderOut(
        id=db_order.id,
        table=db_order.table,
        product=product_out,
        quantity=db_order.quantity
    )

    db.close()
    return order_out

@app.get("/orders/", response_model=list[OrderOut])
def get_all_orders():
    db = SessionLocal()
    orders = db.query(Order).all()
    
    order_list = []
    for order in orders:
        product = db.query(Product).get(order.product_id)
        if product:
            product_out = ProductOut(
                id=product.id,
                name=product.name,
                price=product.price,
            )
            order_out = OrderOut(
                id=order.id,
                table=order.table,
                product=product_out,
                quantity=order.quantity,
            )
            order_list.append(order_out)

    db.close()
    
    return order_list

@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int):
    db = SessionLocal()
    order = db.query(Order).filter(Order.id == order_id).first()
    db.close()
    if order is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    product = db.query(Product).get(order.product_id)
    if product:
        product_out = ProductOut(
                id=product.id,
                name=product.name,
                price=product.price,
            )
        order_out = OrderOut(
            id=order.id,
            table=order.table,
            product=product_out,
            quantity=order.quantity,
        )
        return order_out

    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.get("/orders/table/{table_id}", response_model=OrderResponse)
def get_orders_by_table(table_id: int):
    db = SessionLocal()
    orders = db.query(Order).filter(Order.table == table_id).all()
    if orders is None:
        db.close()
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    total_price = 0.0
    order_list = []
    for order in orders:
        product = db.query(Product).get(order.product_id)
        if product:
            product_out = ProductOut(
                id=product.id,
                name=product.name,
                price=product.price,
            )
            order_out = OrderOut(
                id=order.id,
                table=order.table,
                product=product_out,
                quantity=order.quantity,
            )
            order_list.append(order_out)
            total_price += product.price * order.quantity

    db.close()
    
    response_data = {
        "orders": order_list,
        "total_price": total_price
    }
    
    return OrderResponse(**response_data)

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

@app.post("/orders/table/{table_id}")
def finish_orders_by_table(table_id: int):
    db = SessionLocal()
    orders = db.query(Order).filter(Order.table == table_id).all()
    if not orders:
        db.close()
        raise HTTPException(status_code=404, detail="Esta mesa não possui pedidos")

    total_price = 0.0
    order_list = []
    for order in orders:
        product = db.query(Product).get(order.product_id)
        if product:
            product_out = ProductOut(
                id=product.id,
                name=product.name,
                price=product.price,
            )
            order_out = OrderOut(
                id=order.id,
                table=order.table,
                product=product_out,
                quantity=order.quantity,
            )
            order_list.append(order_out)
            total_price += product.price * order.quantity

    db.close()

    order_history = OrderHistory(
        table=table_id,
        products=', '.join([str(order.product.name) for order in order_list]),
    )

    db = SessionLocal()
    db.add(order_history)
    db.commit()
    db.close()

    db = SessionLocal()
    for order in orders:
        db.delete(order)
    db.commit()
    db.close()

    return {"message": "Pedidos finalizado com sucesso"}

@app.get("/orders/history/", response_model=list[OrderHistoryOut])
def get_all_orders_history():
    db = SessionLocal()
    orders = db.query(OrderHistory).all()
    db.close()
    return orders

@app.get("/health-check")
def health_check():
    return {"status": "ok"}
