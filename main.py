from app.routes.orders import router as orders_router
from app.routes.orders_history import router as orders_history_router
from app.routes.products import router as products_router

from fastapi import FastAPI

app = FastAPI()

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

app.include_router(orders_router)
app.include_router(orders_history_router)
app.include_router(products_router)
