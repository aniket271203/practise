from sqlalchemy import Column, Integer, String, Float, DateTime, select, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apis.order_management_api.app.database import Base

class Product(Base):
    __tablename__="products"
    
    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    price=Column(Float, nullable=False)
    stock=Column(Integer, nullable=False)
    created_at=Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"Product( id={self.id}  name={self.name}  stock={self.stock})"
    

class Order(Base):
    __tablename__="orders"
    
    id=Column(Integer, primary_key=True, index=True)
    user_name=Column(String, nullable=False)
    status=Column(String, nullable=False)
    total_amount=Column(Float,nullable= False)
    created_at=Column(DateTime, default=func.now())
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"Order( id={self.id}  name={self.user_name}  status={self.status})"
    
class OrderItem(Base):
    __tablename__="orderitems"
    
    id=Column(Integer, primary_key=True, index=True)
    order_id=Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id=Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity=Column(Integer, nullable=False)
    price_at_purchase=Column(Float, nullable= False)
    
    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )
    
    def __repr__(self):
        return f"OrderItem( id={self.id}  order_id={self.order_id}  product_id={self.product_id})"