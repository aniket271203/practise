from sqlalchemy import Column, DateTime, Integer, Float, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime,default=func.now())
    
    redemptions=relationship("Redemption",back_populates="user")
    
    def __repr__(self):
        return f"User(id={self.id} name={self.name})"

class Coupon(Base):
    __tablename__="coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code=Column(String,nullable=False,unique=True)
    max_redemptions=Column(Integer,nullable=False)
    remaining_redemptions=Column(Integer,nullable=False)
    discount_percent=Column(Float,nullable=False)
    created_at=Column(DateTime,default=func.now())
    
    fraud_score=Column(Float)
    processed_at=Column(DateTime)
    
    redemptions=relationship("Redemption",back_populates='coupon')
    
    def __repr__(self):
        return f"Coupon(id={self.id} max_redemptions={self.max_redemptions} remaining_redemptions={self.remaining_redemptions} discount_percentage={self.discount_percent})"
    
class Redemption(Base):
    __tablename__="redemptions"
    __table_args__=(UniqueConstraint("user_id","coupon_id"),)
    
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey('users.id'),nullable=False)
    coupon_id=Column(Integer,ForeignKey('coupons.id'),nullable=False)
    created_at=Column(DateTime,default=func.now())
    
    user=relationship('User',back_populates='redemptions')
    coupon=relationship('Coupon',back_populates="redemptions")
    
    def __repr__(self):
        return f"Redemption(id={self.id} user_id={self.user_id} coupon_id={self.coupon_id})"