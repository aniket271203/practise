from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from apis.trader_api.app.database import Base


class Trader(Base):
    __tablename__ = "traders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    trades=relationship('Trade', back_populates='trader')
    positions=relationship('Position', back_populates='trader')

    def __repr__(self):
        return f"Trader(id={self.id} name={self.name})"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey("traders.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    side = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    trader=relationship('Trader', back_populates='trades')

    def __repr__(self):
        return f"Trade(id={self.id} symbol={self.symbol} side={self.side})"


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey("traders.id"), nullable=False)
    symbol = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    trader=relationship('Trader', back_populates='positions')
    
    def __repr__(self):
        return f"Position(id={self.id} symbol={self.symbol})"
