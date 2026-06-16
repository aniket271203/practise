from enum import Enum
import sqlite3, aiosqlite
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, func
import math
from random import randint
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
import datetime

class OrderStatus(str,Enum):
    PENDING="pending"
    CONFIRMED="confirmed"
    CANCELLED="cancelled"

class Order:
    
    id:int
    customer_id:int
    amount:float
    status:OrderStatus
    created_at:str

# this is in sqlite
async def get_order_summary():
    async with aiosqlite.connect('orders.db') as db:
        result= await db.execute("""
                                 SELECT 
                                 COUNT(*) AS total_orders,
                                 SUM(amount) AS total_revenue,
                                 SUM(CASE WHEN status="confirmed" THEN 1 ELSE 0 END) AS confirmed_orders,
                                 SUM(CASE WHEN status="cancellled" THEN 1 ELSE 0 END) AS cancelled_orders
                                 FROM orders
                                 """)
        rows=await result.fetchall()
        
        return {
        "total_orders": rows.total_orders,
        "total_revenue": rows.total_revenue,
        "confirmed_orders": rows.confirmed_orders,
        "cancelled_orders": rows.cancelled_orders
    }

# in sqlalchemy
async def get_order_summary_sqlalchemy(db:AsyncSession):
    result=await db.execute(select(
        func.count(Order.id).label("total_orders"),
        func.sum(Order.amount).label("total_revenue"),
        func.sum(case((Order.status==OrderStatus.CONFIRMED,1),else_=0)).label("confirmed_orders"),
        func.sum(case((Order.status==OrderStatus.CANCELLED,1),else_=0)).label("cancelled_orders")
    ))
    rows=result.first()

    return {
        "total_orders": rows.total_orders,
        "total_revenue": rows.total_revenue,
        "confirmed_orders": rows.confirmed_orders,
        "cancelled_orders": rows.cancelled_orders
    }


async def get_top_customers(limit=10):
    async with aiosqlite.connect('orders.db') as db:
        cur=await db.execute("""
                             SELECT customer_id,
                             SUM(amount) AS total_spent
                             FROM orders 
                             GROUP BY customer_id
                             ORDER BY total_spent
                             LIMIT=?
                             """,(limit))
        rows=await cur.fetchall()
        
        return rows

def random_factor():
    return randint(0,1)

def compute_risk_score(amount:float)->float:
    return math.log(amount+1)*random_factor()

def chunk_lists(items,n_workers):
    size=(len(items)+n_workers-1)//n_workers
    return [items[i:i+size] for i in range(0,len(items),size)]

def process_chunk(rows):
    results=[]
    for row in rows:
        id, customer_id, amount, status, created_at =row
        risk_score=compute_risk_score(float(amount))
        processed_at=datetime.utcnow().isoformat()
        results.append((risk_score,processed_at,int(id)))
    return results

def read_db_chunks(chunk_size=10000):
    with sqlite3.connect('orders.db') as db:
        last_id=0
        while True:
            rows=db.execute("""
                            SELECT * 
                            FROM orders
                            WHERE id>?
                            ORDER BY id
                            LIMIT ?
                            """,(last_id,chunk_size)).fetchall()
            if not rows:
                break
            last_id=rows[-1][0]
            yield rows
Jobs={}

def run_ingest(job_id:str):
    try:
        db=sqlite3.connect('orders.db')
        db.execute("""
                ALTER TABLE orders ADD COLUMN risk_score REAL;
                ALTER TABLE orders ADD COLUMN processed_at DATETIME;
                    """)
        
        with ProcessPoolExecutor(max_workers=cpu_count()) as pool:
            for rows in read_db_chunks():
                chunks=chunk_lists(rows,cpu_count())
                
                results=pool.map(process_chunk,chunks)
                
                flattened=[]
                for chunk_results in results:
                    flattened.extend(chunk_results)
                
                db.executemany("UPDATE orders SET risk_score=?,processed_at=? WHERE id=?",flattened)
        
            db.commit()
        db.close()
        Jobs[job_id]={"status":"completed"}
    except Exception as e:
        Jobs[job_id]={"status":"failed", "error":e}
        raise e
    # or do whatever you want to do
    finally:
        if db:
            db.close()
