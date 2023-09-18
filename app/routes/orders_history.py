from app.db import SessionLocal
from app.models.orders_history import OrderHistory, OrderHistoryOut

from fastapi import APIRouter

router = APIRouter()

@router.get("/orders/history/", response_model=list[OrderHistoryOut])
def get_all_orders_history():
    db = SessionLocal()
    orders = db.query(OrderHistory).all()
    db.close()
    return orders