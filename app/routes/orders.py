from app.db.models import Product, Order, OrderHistory
from app.schemas.orders import OrderCreate, OrderOut, OrderResponse, ProductOut
from app.db.connection import Session

from fastapi import APIRouter, HTTPException

from typing import List

router = APIRouter(tags=["Pedidos"])


@router.post("/orders/", response_model=OrderOut)
def create_order(order: OrderCreate):
    db = Session()

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


@router.get("/orders/", response_model=List[OrderOut])
def get_all_orders():
    db = Session()
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


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int):
    db = Session()
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


@router.get("/orders/table/{table_id}", response_model=OrderResponse)
def get_orders_by_table(table_id: int):
    db = Session()
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


@router.put("/orders/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order: OrderCreate):
    db = Session()
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


@router.delete("/orders/{order_id}")
def delete_order(order_id: int):
    db = Session()
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    db.delete(db_order)
    db.commit()
    db.close()
    return {"message": "Pedido removido com sucesso"}


@router.post("/orders/table/{table_id}")
def finish_orders_by_table(table_id: int):
    db = Session()
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

    db = Session()
    db.add(order_history)
    db.commit()
    db.close()

    db = Session()
    for order in orders:
        db.delete(order)
    db.commit()
    db.close()

    return {"message": "Pedidos finalizado com sucesso"}
