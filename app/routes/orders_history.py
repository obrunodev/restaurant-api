from app.db.connection import Session
from app.db.models import OrderHistory
from app.schemas.orders_history import OrderHistoryOut

from fastapi import APIRouter

from typing import List

router = APIRouter(tags=["Histórico de pedidos"])


@router.get("/orders/history/", response_model=List[OrderHistoryOut])
def get_all_orders_history():
    db = Session()
    orders = db.query(OrderHistory).all()
    db.close()
    return orders
