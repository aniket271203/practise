from pydantic import BaseModel, validator
from enum import Enum
from typing import List

class OrderStatus(str,Enum):
    PENDING="pending"
    CONFIRMED="confirmed"
    CANCELLED="cancelled"

class ProductCreate(BaseModel):
    
    name:str
    price:float
    stock:int
    
    @validator('price')
    def check_price(cls,v):
        if v<=0:
            raise ValueError("price must be a positive value")
        return v
    
    @validator('stock')
    def check_stock(cls,v):
        if v<0:
            raise ValueError("stock must be a positive value")
        return v
       
    
class OrderItemCreate(BaseModel):
    
    product_id:int
    quantity:int

class ProductResponse(BaseModel):
    
    id:int
    name:str
    price:float
    stock:int
    
    class Config:
        from_attributes=True


class OrderCreate(BaseModel):
    
    user_name:str
    items:List[OrderItemCreate]
    

class OrderResponse(BaseModel):
    
    id:int
    user_name:str
    status:OrderStatus
    total_amount:float
    
    class Config:
        from_attributes=True
        