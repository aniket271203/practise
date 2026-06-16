from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    mobile=Column(Integer)

    inventorys = relationship('Inventory', back_populates='warehouse')

    shipments = relationship('Shipment', back_populates='warehouse')

    def __repr__(self):
        return f" Warhouse(id={self.id} name={self.name} location={self.location})"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

    inventorys = relationship('Inventory', back_populates='product')

    shipments = relationship('Shipment', back_populates='product')

    def __repr__(self):
        return f" Product(id={self.id} name={self.name} price={self.price})"


class Inventory(Base):
    __tablename__ = "inventorys"
    __table_args__ = (UniqueConstraint('warehouse_id', 'product_id'),)

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    risk_score = Column(Float)
    processed_at = Column(DateTime)

    product = relationship('Product', back_populates='inventorys')

    warehouse = relationship('Warehouse', back_populates='inventorys')

    def __repr__(self):
        return f" Inventory(id={self.id} warehouse_id={self.warehouse_id} product_id={self.product_id} quantity={self.quantity} risk_score={self.risk_score} processed_at={self.processed_at})"


class Shipment(Base):
    __tablename__ = "shipments"
    __table_args__ = (UniqueConstraint('warehouse_id', 'product_id'),)

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    product = relationship('Product', back_populates='shipments')

    warehouse = relationship('Warehouse', back_populates='shipments')

    def __repr__(self):
        return f" Shipment(id={self.id} warehouse_id={self.warehouse_id} product_id={self.product_id} quantity={self.quantity} status={self.status})"
