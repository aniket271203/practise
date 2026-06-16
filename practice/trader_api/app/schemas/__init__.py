from pydantic import BaseModel, validator
from enum import Enum
from email_validator import validate_email

class TraderCreate(BaseModel):
    
    name:str
    email:str
    
    @validator('name')
    def check_name(cls,v):
        if not v.isalpha():
            raise ValueError("name must contain only letters")
        return v
    
    @validator('email')
    def check_email(cls,v):
        if not validate_email(v):
            raise ValueError("email must be valid")
        return v
    
class TraderResponse(BaseModel):
    
    id:int
    name:str
    
    class Config:
        from_attributes=True

class PositionCreate(BaseModel):
    
    trader_id:int
    symbol:str
    quantity:int
    average_price:float
    
    @validator('symbol')
    def symbol_must_be_letters(cls,v):
        if not v.isalpha():
            raise ValueError("symbol must be only letters")
        return v.upper()
    
    @validator('quantity')
    def quantity_must_be_positive(cls,v):
        if v<0:
            raise ValueError("quantity must be positive")
        return v
    
    @validator('average_price')
    def price_must_be_positive(cls,v):
        if v<0:
            raise ValueError("price must be positive")
        return v
    
class PositionResponse(BaseModel):
    
    id:int
    trader_id:int
    symbol:str
    quantity:int
    average_price:float
    
    class Config:
        from_attributes=True
        
class TradeSide(str,Enum):
    BUY="buy"
    SELL="sell"
        
class TradeCreate(BaseModel):
    
    trader_id:int
    symbol:str
    quantity:int
    price:float
    
    @validator('symbol')
    def symbol_must_be_letters(cls,v):
        if not v.isalpha():
            raise ValueError("symbol must be only letters")
        return v.upper()
    
    @validator('quantity')
    def quantity_must_be_positive(cls,v):
        if v<0:
            raise ValueError("quantity must be positive")
        return v
    
    @validator('price')
    def price_must_be_positive(cls,v):
        if v<0:
            raise ValueError("price must be positive")
        return v

class TradeResponse(BaseModel):
    
    id:int
    trader_id:int
    symbol:str
    quantity:int
    price:float
    side:TradeSide
    
    class Config:
        from_attributes=True
        
class TraderSummary(BaseModel):
    trader_id:int
    total_positions:int
    total_trades:int
    portfolio_value:float
    
    class Config:
        from_attributes=True