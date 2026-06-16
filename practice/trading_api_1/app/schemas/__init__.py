from pydantic import validator, BaseModel
from enum import Enum

class TradeStatus(str,Enum):
    PENDING="pending"
    FILLED="filled"
    CANCELLED="canceled"

class TradeCreate(BaseModel):
    symbol: str
    quantity: int
    price: float
    
    @validator('symbol')
    def symbol_must_be_valid(cls,v):
        if not v.isalpha():
            raise ValueError("symbol must contain only letters")
        return v.upper()
    
    @validator('quantity')
    def quantity_must_be_positive(cls,v):
        if v<=0:
            raise ValueError("quantity must be a positive value")
        return v
        
    @validator('price')
    def price_must_be_positive(cls,v):
        if v<=0:
            raise ValueError("price must be a positive value")
        return v

class TradeResponse(BaseModel):
    id:int
    symbol:str
    quantity:int
    price:float
    status:TradeStatus
    
    class config: 
        from_attributes= True