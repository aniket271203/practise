from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select, case, func, desc
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer,String,Float

DATABASE_URL="sqlite+aiosqlite:///./trades.db"

engine=create_async_engine(DATABASE_URL)

AsyncLocalSession=async_sessionmaker(
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
            
class Trade(Base):
    __tablename__="trades"
    
    id=Column(Integer,primary_key=True, index=True)
    trader_id=Column(Integer,nullable=False)
    symbol=Column(String,nullable=False)
    quantity=Column(Integer,nullable=False)
    price=Column(Float,nullable=False)
    side=Column(String,nullable=False)
    
    def __repr__(self):
        return f"Trade( id={self.id} trader_id={self.trader_id} side={self.side})"
    
async def get_total_traded_value(db:AsyncSession=get_db()):
    cur=await db.execute(select(func.sum(Trade.price*Trade.quantity).label("total_value")))
    result=cur.first()
    return {
        "total_value":result.total_value
    }

async def get_symbol_summary(db:AsyncSession=get_db()):
    cur=await db.execute(select(Trade.symbol,func.sum(Trade.quantity*Trade.price).label('volume')).group_by(Trade.symbol))
    results=cur.all()
    return results

async def get_top_5_symbols(db:AsyncSession=get_db()):
    cur=await db.execute(select(Trade.symbol,func.sum(Trade.quantity*Trade.price).label('volume')).group_by(Trade.symbol).order_by(desc('volume')).limit(5))
    results=cur.all()
    return results

async def get_trader_summary(trader_id:int,db:AsyncSession=get_db()):
    cur= await db.execute(select(
        func.count(Trade.id).label('total_trades'),
        func.sum(case((Trade.side=='buy',1),else_=0)).label('buy_count'),
        func.sum(case((Trade.side=='sell',1),else_=0)).label('sell_count'),
        func.sum(Trade.price*Trade.quantity).label("total_volume")
    ).where(Trade.trader_id==trader_id))
    results=cur.first()
    return {
    "total_trades": results.total_trades,
    "buy_count": results.buy_count,
    "sell_count": results.sell_count,
    "total_volume": results.total_volume
    }
    
# WINDOW FUNCTION
# For every trade:
# show trade value
# and running cumulative value

async def get_running_cumulative(db:AsyncSession):
    cur=await db.execute(select(
        Trade.id.label("id"),
        func.sum(Trade.price*Trade.quantity).label('trade_value'),
        func.sum(Trade.price*Trade.quantity).over(order_by=Trade.id).label('running_total')
    ))
    results=cur.scalars().all()
    
    # sql
    # db.execute("""
    #            SELECT id,
    #            SUM(price*quantity) AS trade_value,
    #            SUM(price*quantity)  
    #            OVER(ORDER BY id) AS running_total
    #            FROM trades
    #            """)
    return results

## ASIGNMENT 8 RACE CONDITION


class Position(Base):
    __tablename__="positions"
    
    id=Column(Integer,primary_key=True,index=True)
    symbol=Column(String,nullable=False)
    quantity=Column(Integer,nullable=False)

    def __repr__(self):
        return f"Position(id={self.id} symbol={self.symbol})"

async def sell_position(id:int,sell_qty:int,db:AsyncSession=get_db()):
    position=await db.execute(select(Position).where(Position.id==id).with_for_update())

    position= position.scalar_one_or_none()
    if position.quantity<sell_qty:
        raise ValueError()
    position.quantity-=sell_qty
    
    await db.flush()
    return 
    

import threading

lock=threading.Lock()

#assignment 9  Producer Consumer

"""
we define these as 
Producer:
read chunks and 
add chunk to Queue


Consumer:
get chunk from queue and
process Chunk
"""

from multiprocessing import Queue, Process
import sqlite3
import math

def read_db_chunks(chunk_size=100000):
    with sqlite3.connect("trades.db") as db:
        last_id=0
        while True:
            
            rows=db.execute("""
                        SELECT *
                        FROM trades
                        WHERE id>?
                        ORDER BY id
                        LIMIT ?        
                            """,(last_id,chunk_size)).fetchall()

            if not rows:
                break
            last_id=rows[-1][0]
            yield(rows)

def producer(queue):
    for chunk in read_db_chunks():
        queue.put(chunk)
        
    queue.put(None)

def compute_risk_score(price:float,qty:int):
    return math.log(price*qty*0.1)

def process_chunk(rows):
    results=[]
    for row in rows:
        id,symbol,price,qty,side=row
        risk_score=compute_risk_score(float(price),int(qty))
        results.append((risk_score,int(id)))
    return results

def consumer(queue):
    while True:
        chunk=queue.get()
        if chunk is None:
            break
        process_chunk(chunk)
        
def main():
    queue=Queue()
    
    p1=Process(target=producer,args=(queue,))
    p2=Process(target=consumer,args=(queue,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    # we can move ahead without the use of locks if needed they will be needed for in row loaking in case of databse if multiple consumers try updating the same row at the same time 
    
    
    