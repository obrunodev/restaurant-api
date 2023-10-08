from pydantic import BaseModel


class OrderHistoryCreate(BaseModel):
    table: int
    products: str


class OrderHistoryOut(BaseModel):
    id: int
    table: int
    products: str
