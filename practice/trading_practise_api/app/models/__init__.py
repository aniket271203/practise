from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from apis.trading_practise_api.app.database import Base

class Trader(Base):
    __tablename__="traders"
    
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    email=Column(String,nullable=False)
    desk=Column(String,nullable=False)
    is_active=Column(Boolean,nullable=False, default=True)
    created_at=Column(DateTime,default=func.now())
    
    trades=relationship("Trade",back_populates="trader")
    
    def __repr__(self):
        return f"Trader(id={self.id} name={self.name} is_active={self.is_active})"
    
class Trade(Base):
    __tablename__='trades'
    
    id=Column(Integer,primary_key=True,index=True)
    symbol=Column(String,nullable=False,index=True)
    quantity=Column(Integer,nullable=False)
    price=Column(Float,nullable=False)
    side=Column(String,nullable=False)
    status=Column(String,nullable=False)
    exchange=Column(String,nullable=False)
    
    trader_id=Column(Integer,ForeignKey('traders.id'),nullable=False)
    
    created_at=Column(DateTime,default=func.now())
    updated_at=Column(DateTime,server_default=func.now(),onupdate=func.now())
    
    trader= relationship("Trader", back_populates='trades')
    
    def __repr__(self):
        return f"Trade(id={self.id} symbol={self.symbol} status={self.status})"
    
    