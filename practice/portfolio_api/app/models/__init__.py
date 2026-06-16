from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from apis.portfolio_api.app.database import Base

class Position(Base):
    __tablename__="positions"
    
    id=Column(Integer,primary_key=True, index=True)
    symbol=Column(String,index=True, nullable=False)
    quantity=Column(Integer, nullable=False)
    avg_price=Column(Float, nullable=False)
    created_at=Column(DateTime,default=func.now())
    updated_at=Column(DateTime,server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"Position(id={self.id}, symbol={self.symbol})"
    