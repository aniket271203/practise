from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import select,update, case, func, Column, Integer, String, Float, DateTime, ForeignKey
from fastapi import HTTPException
from enum import Enum
import aiosqlite

DATABASE_URL = "sqlite+aiosqlite:///./practise.db"

engine = create_async_engine(DATABASE_URL)

AsyncLocalSession = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncLocalSession() as session:
        try:
            yield session
        finally:
            await session.close()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stock = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    reservations = relationship("Reservation", back_populates="product")

    def __repr__(self):
        return f"Product(id={self.id} name={self.name})"


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, nullable=False)

    product = relationship('Product', back_populates="reservations")

    def __repr__(self):
        return f"Reservation(id={self.id} product_id={self.product_id} status={self.status})"


class ReservationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


async def create_reservation(product_id: int, quantity: int, db: AsyncSession = get_db()):
    async with db.begin():
        result = await db.execute(select(Product).where(Product.id == product_id).with_for_update())
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )
        if product.stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"cannot reserve more than available product quantity| avaialable={product.stock}"
            )
        product.stock -= quantity

        reservation = Reservation(
            product_id=product_id,
            quantity=quantity,
            status=ReservationStatus.ACTIVE
        )
        db.add(reservation)
        await db.flush()
        await db.refresh(reservation)

        return reservation


async def cancel_reservation(reservation_id: int, db: AsyncSession = get_db()):
    async with db.begin():
        result = await db.execute(select(Reservation).where(Reservation.id == reservation_id).with_for_update())
        reservation = result.scalar_one_or_none()
        if not reservation:
            raise HTTPException(
                status_code=404,
                detail="reservation not found"
            )
        if reservation.status == ReservationStatus.CANCELLED:
            raise HTTPException(
                status_code=400,
                detail="Reservation Already cancelled"
            )
        if reservation.status == ReservationStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel completed reservation"
            )
        result = await db.execute(select(Product).where(Product.id == reservation.product_id).with_for_update())
        product = result.scalar_one_or_none()
        product.stock += reservation.quantity
        reservation.status = ReservationStatus.CANCELLED

        await db.flush()
        await db.refresh(reservation)

        return reservation


async def get_inventory_summary(db: AsyncSession = get_db()):
    # if different tables have to be accessed then execute on different tables and then return ans
    cur = await db.execute(select(
        func.count(Product.id).label('total_products'),
        func.sum(Product.stock).label('total_stock'),
    ))
    results = cur.first()
    
    cur = await db.execute(
        select(func.count(Reservation.id).label("active_reservations")).where(
            Reservation.status == ReservationStatus.ACTIVE)
    )
    
    active_reservation=cur.first()
    return {
        "total_products": results.total_products,
        "total_stock": results.total_stock,
        "active_reservations": active_reservation.active_reservations
    }


def compute_risk_score(price: float, quantity: int) -> float:
    return price*quantity


def chunk_list(items, n_workers):
    size = (len(items)+n_workers-1)//n_workers
    return [items[i:i+size] for i in range(0, len(items), size)]

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
import sqlite3

def read_db_chunk(chunk_size=10000):
    db=sqlite3.connect('practise.db')
    last_id=0
    while True:
        cur= db.execute(select(Reservation.id.label('id'),
                               Product.price.label('price'),
                               Reservation.quantity.label('quantity'))
                        .select_from(Reservation)
                        .join(Product,Product.id==Reservation.product_id)
                        .where(Reservation.id>last_id)
                        .order_by(Reservation.id)
                        .limit(chunk_size))
        reservations=cur.fetchall()
        if not reservations:
            break        
        last_id=reservations[-1][0]
        yield reservations
    db.close()

def process_chunk(rows):
    results=[]
    for row in rows:
        id,price,quantity=row
        risk_score=compute_risk_score(float(price),int(quantity))
        results.append((risk_score,int(id)))
    return results

def process_reservation_risk(db=get_db()):
    with ProcessPoolExecutor(max_workers=cpu_count()) as pool:
        for chunk in read_db_chunk():
            chunks=chunk_list(chunk,cpu_count())
            
            chunk_results=pool.map(process_chunk,chunks) 
            flattened=[]
            
            for chunk in chunk_results:
                flattened.extend(chunk)
        
            db=sqlite3.connect('practice.db')
            db.executemany("""
                        UPDATE reservations
                        SET risk_score=?
                        WHERE id=?
                        """,flattened)
        db.commit()
        