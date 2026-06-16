from apis.trading_api.app.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    def __repr__(self):
        return f"Trade(id={self.id}, symbol={self.symbol}, status={self.status})"
