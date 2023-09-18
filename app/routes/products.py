from app.db import SessionLocal
from app.models.products import Product, ProductOut, ProductCreate

from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/products/", response_model=ProductOut)
def create_product(product: ProductCreate):
    db = SessionLocal()
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

@router.get("/products/", response_model=list[ProductOut])
def get_all_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@router.put("/products/{product_id}", response_model=ProductOut)
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

@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(db_product)
    db.commit()
    db.close()
    return {"message": "Produto removido com sucesso"}