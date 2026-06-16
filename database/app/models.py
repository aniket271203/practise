from sqlalchemy import Column,Integer,Float,String
from database import Base

class Trade(Base):
    
    id=Column(Integer,primary_key=True,index=True)
    symbol=Column(String,index=True,nullable=False)
    quantity=Column(Integer,nullable=False)
    price=Column(Float,nullable=False)
    side=Column(String,nullable=False)
    
    def __repr__(self):
        return f"Trade( id={self.id} symbol={self.symbol} side={self.side})"
