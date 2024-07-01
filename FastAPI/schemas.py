# schemas.py
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: int

    class Config:
        from_attributes = True
