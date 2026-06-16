from apis.trading_api_1.app.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.sql import func

class Trade:
    __tablename__="trades"
    
    id=Column(Integer, primary_key=True, index=True)
    symbol=Column(String,index=True,nullable=False)
    quantity=Column(Integer,nullable=False)
    price=Column(Float, nullable=False)
    status=Column(String, nullable=False)
    created_at=Column(DateTime, default=func.now())
    updated_at=Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"Trade_id={self.id}, Trade_symbol={self.symbol}, status={self.status}"
    