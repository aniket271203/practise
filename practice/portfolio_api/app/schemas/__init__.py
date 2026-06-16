from pydantic import BaseModel, validator

# PositionResponse, PositionCreate

class PositionCreate(BaseModel):
    symbol:str
    quantity:int
    avg_price:float
    
    @validator('symbol')
    def check_valid_symbol(cls,v):
        if not v.isalpha():
            raise ValueError("symbol must contain only letters")
        return v.upper()
    
    @validator('quantity')
    def quantity_must_be_positive(cls,v):
        if v<=0:
            raise ValueError("quantity must be positive")
        return v
    
    @validator('avg_price')
    def price_must_be_positive(cls,v):
        if v<0:
            raise ValueError("avg_price must be positive")
        return v
    

class PositionResponse(BaseModel):
    id:int
    symbol:str
    quantity:int
    avg_price:float
    
    class config: 
        from_attributes= True