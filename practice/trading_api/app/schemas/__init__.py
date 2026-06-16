from pydantic import BaseModel, validator
from enum import Enum

class TradeStatus(str,Enum):
    # the enum defination ofr different status that the trade can be in 
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    
class TradeCreate(BaseModel):
    # the format we expect from the user and teh validators make sure the values we expect are correct or not by defining them as validators pydantic will atomatically check them each time an entry comes from teh user 
    symbol: str
    quantity: int
    price: float

    @validator('symbol')
    def symbol_must_be_valid(cls, v):
        if not v.isalpha():
            raise ValueError('symbol must only contain letter')
        return v.upper()
    
    @validator('price')
    def price_must_be_positive(cls,v):
        if v<=0:
            raise ValueError('price must be positive')
        return v
    
    @validator('quantity')
    def qauntity_must_be_non_negative(cls,v):
        if v<0:
            raise ValueError('quantity must be positive')
        return v
    
class TradeResponse(BaseModel):
    # to define teh response struct for the client basically what the server will send as a response
    id: int
    symbol: str
    quantity: int
    price: float
    status: TradeStatus
    
    class config: 
        from_attributes= True
        
