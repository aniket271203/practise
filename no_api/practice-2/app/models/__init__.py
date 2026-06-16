from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Trader(Base):
    __tablename__="traders"
    
    id=Column(Integer,primary_key=True, index=True)
    name=Column(String,nullable= False)
    cash_balance=Column(Float,nullable=False)
    created_at=Column(DateTime,default=func.now())
    
    trades=relationship('Trade', back_populates='trader')
    positions=relationship("Position",back_populates='trader')

    def __repr__(self):
        return f"Trader(id={self.id} name={self.name} cash_balance={self.cash_balance})"
    
class Trade(Base):
    __tablename__="trades"
    
    id=Column(Integer,primary_key=True,index=True)
    trader_id=Column(Integer,ForeignKey("traders.id"),nullable=False)
    symbol=Column(String,index=True,nullable=False)
    quantity=Column(Integer,nullable=False)
    price=Column(Float,nullable=False)
    side=Column(String,nullable=False)
    created_at=Column(DateTime,default=func.now())
    
    trader=relationship('Trader', back_populates='trades')
    
    def __repr__(self):
        return f"Trade(id={self.id} trader_id={self.trader_id} price={self.price} quantity={self.quantity} symbol={self.symbol} side={self.side})"

class Position(Base):
    __tablename__="positions"
    __table_args__=(UniqueConstraint("trader_id","symbol"),)
    
    id=Column(Integer,primary_key=True,index=True)
    trader_id=Column(Integer,ForeignKey('traders.id'),nullable=False)
    symbol=Column(String,nullable=False,index=True)
    quantity=Column(Integer,nullable=False)
    average_price=Column(Float,nullable=False)
    risk_score=Column(Float)
    processed_at=Column(DateTime)
    
    trader=relationship("Trader", back_populates='positions')
    
    def __repr__(self):
        return f"Position(id={self.id} trader_id={self.trader_id} symbol={self.symbol} quantity={self.quantity} average_price={self.average_price} risk_score={self.risk_score} processed_at={self.processed_at})"