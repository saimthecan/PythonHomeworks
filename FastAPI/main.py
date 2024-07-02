from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import database
from contextlib import asynccontextmanager

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/products/", response_model=List[schemas.Product])
def read_products(
    page: int = Query(1, ge=1),  # Varsayılan değer 1, en az 1 olmalı
    db: Session = Depends(get_db)
):
    count = 3  # Her sayfada gösterilecek ürün sayısı
    offset = (page - 1) * count
    products = db.query(models.Product).order_by(models.Product.id).offset(offset).limit(count).all()
    return products

@app.get("/favicon.ico")
async def favicon():
    return ""

def add_sample_products(db: Session):
    for i in range(1, 51):
        product = models.Product(
            name=f"Product {i}",
            description=f"Description for product {i}",
            price=i * 10
        )
        db.add(product)
    db.commit()

@asynccontextmanager
async def lifespan_context(app: FastAPI):
    db = next(get_db())
    add_sample_products(db)
    db.close()
    yield

app.router.lifespan = lifespan_context
