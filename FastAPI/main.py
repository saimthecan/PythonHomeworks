from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import models
import schemas
import database
from contextlib import asynccontextmanager
import json
import os

# Initialize the database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency to get a database session
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
    page: int = Query(1, ge=1),  # Default value 1, must be at least 1
    db: Session = Depends(get_db)
):
    count = 3  # Number of products per page
    offset = (page - 1) * count

    # Check the total number of products
    total_products = db.query(models.Product).count()

    if offset >= total_products:
        return []

    products = db.query(models.Product).order_by(models.Product.id).offset(offset).limit(count).all()
    return products

class FilterParams(BaseModel):
    page: int = 1
    divisor: int

@app.post("/products/filter", response_model=List[schemas.Product])
def read_products(filter_params: FilterParams, db: Session = Depends(get_db)):
    count = 3  # Number of products per page
    offset = (filter_params.page - 1) * count

    # Check the total number of products that match the filter
    total_products = db.query(models.Product).filter(models.Product.price % filter_params.divisor == 0).count()

    if offset >= total_products:
        return []

    products = (
        db.query(models.Product)
        .filter(models.Product.price % filter_params.divisor == 0)
        .order_by(models.Product.id)
        .offset(offset)
        .limit(count)
        .all()
    )
    return products

class NewProduct(BaseModel):
    name: str
    description: str
    price: int

@app.post("/add_product/")
def add_product(new_product: NewProduct, db: Session = Depends(get_db)):
    # Add the new product to the database
    product = models.Product(**new_product.dict())
    db.add(product)
    db.commit()
    db.refresh(product)

    # Add the new product to a text file with its ID
    product_data_with_id = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price
    }
    with open("products.txt", "a", encoding="utf-8") as file:
        file.write(json.dumps(product_data_with_id, ensure_ascii=False) + "\n")

    return {"message": "Product added successfully", "product": product_data_with_id}

@app.delete("/clear_database")
def clear_database(db: Session = Depends(get_db)):
    db.query(models.Product).delete()
    db.commit()
    return {"message": "Database cleared successfully"} 

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    # Delete the product from the database
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()

    # Delete the product from the text file
    if os.path.exists("products.txt"):
        with open("products.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open("products.txt", "w", encoding="utf-8") as file:
            for line in lines:
                product_data = json.loads(line.strip())
                if product_data["id"] != product_id:
                    file.write(json.dumps(product_data, ensure_ascii=False) + "\n")

    return {"message": f"Product with ID {product_id} deleted"}

# Function to add sample products from the file to the database
def add_sample_products(db: Session):
    if not os.path.exists("products.txt"):
        return

    with open("products.txt", "r", encoding="utf-8") as file:
        product_count = 0  # Counter to keep track of products
        for line in file:
            product_data = json.loads(line.strip())
            product = models.Product(**product_data)
            db.add(product)
            product_count += 1  # Increment counter for each product added
        db.commit()

@app.post("/restore_products/")
def restore_products(db: Session = Depends(get_db)):
    add_sample_products(db)
    return {"message": "Products restored from products.txt"}

@asynccontextmanager
async def lifespan_context(app: FastAPI):
    async with app.state.db() as db:
        add_sample_products(db)
    yield

app.router.lifespan = lifespan_context

# Initialize database connection in app state
@app.on_event("startup")
async def startup_event():
    app.state.db = get_db()

# New class for updating product price
class UpdateProductPrice(BaseModel):
    price: int

@app.put("/update_product_price/{product_id}")
def update_product_price(product_id: int, update_data: UpdateProductPrice, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.price = update_data.price
    db.commit()
    db.refresh(product)

    # Update the product price in the text file
    if os.path.exists("products.txt"):
        with open("products.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open("products.txt", "w", encoding="utf-8") as file:
            for line in lines:
                product_data = json.loads(line.strip())
                if product_data["id"] == product_id:
                    product_data["price"] = update_data.price
                file.write(json.dumps(product_data, ensure_ascii=False) + "\n")

    return {"message": "Product price updated successfully", "product": product}

