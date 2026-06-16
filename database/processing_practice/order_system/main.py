from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from fastapi import FastAPI, HTTPException, BackgroundTasks
import csv
import math
import uuid
import sqlite3
import aiosqlite
from typing import List
from enum import Enum


class OrderStatus(str, Enum):
    CANCELLED = "cancelled"
    FILLED = "filled"
    NEW = "new"


Jobs = {}

process_executor = ProcessPoolExecutor(max_workers=cpu_count())

app = FastAPI()


def chunk_list(items: List, n_workers: int):
    size = (len(items)+n_workers-1)//n_workers
    return [items[i:i+size] for i in range(0, len(items), size)]


def compute_latency_score(price: float, qty: int) -> float:
    notional = price * qty
    score = 0.0
    for i in range(1, 200):
        score += math.sin(notional / i) * math.log(i + 1)
    return round(score, 6)


def process_chunk(rows):
    results = []
    for row in rows:
        order_id, symbol, side, price, qty, status, timestamp = row
        price, qty = float(price), int(qty)
        latency_score = compute_latency_score(price, qty)
        results.append((int(order_id), symbol, side, price,
                       qty, status, timestamp, latency_score))
    return results


def run_ingest(job_id: str):
    with open("orders.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

    chunks = chunk_list(rows, cpu_count())

    chunk_results = process_executor.map(process_chunk, chunks)

    row_results = [r for chunk in chunk_results for r in chunk]

    conn = sqlite3.connect('orders.db')
    conn.executemany("INSERT INTO orders VALUES(?,?,?,?,?,?,?,?)", row_results)
    conn.commit()
    conn.close()

    Jobs[job_id] = {"status": "completed", "rows": len(row_results)}


@app.get('/analytics/fill-rate')
async def get_fill_rate():
    async with aiosqlite.connect('orders.db') as db:
        cur = await db.execute("""
                               SELECT symbol,
                               100*SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END)/COUNT(*) AS Cancelled_pct,
                               100*SUM(CASE WHEN status='filled' THEN 1 ELSE 0 END)/COUNT(*) AS filled_pct,
                               100*SUM(CASE WHEN status='new' THEN 1 ELSE 0 END)/COUNT(*) AS new_pct
                               FROM orders
                               GROUP BY symbol
                               """)
        results=await cur.fetchall()
        
        cols=[d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in results]
    
@app.get('/analytics/top-symbols')
async def get_top_symbol():
    async with aiosqlite.connect('orders.db') as db:
        cur=await db.execute("""
                       SELECT symbol,
                       SUM(CASE WHEN status='filled' THEN 1 ELSE 0 END) AS filled
                       FROM orders
                       GROUP BY symbol
                       ORDER BY filled DESC
                       LIMIT 5
                       """)
        results=await cur.fetchall()
        
        cols=[d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in results]
        

@app.get('/analytics/order-funnel/{symbol}')
async def order_funnel(symbol:str):
    async with aiosqlite.connect('orders.db') as db:
        cur=await db.execute("""WITH status_counts AS (
            SELECT
                symbol,
                SUM(CASE WHEN status='NEW' THEN 1 ELSE 0 END) AS new_count,
                SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END) AS filled_count,
                SUM(CASE WHEN status='CANCELLED' THEN 1 ELSE 0 END) AS cancelled_count
            FROM orders
            WHERE symbol = ?
            GROUP BY symbol
        ),
        fill_times AS (
            SELECT
                AVG(
                    (julianday(f.timestamp) - julianday(n.timestamp))
                    * 86400
                ) AS avg_fill_seconds
            FROM orders n
            JOIN orders f
                ON n.order_id = f.order_id
            WHERE n.status='NEW'
            AND f.status='FILLED'
            AND n.symbol=?
        )
        SELECT *
        FROM status_counts
        CROSS JOIN fill_times;
                            """)
        
        rows=await cur.fetchall()
        
        cols=[d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in rows]



@app.post('/reprocess', status_code=202)
async def start_ingestion(bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    Jobs[job_id] = {"status": "running"}
    bg.add_task(run_ingest, job_id)
    return {"job_id": job_id, "status": "running"}


@app.get('/reprocess/{job_id}')
async def get_status(job_id: str):
    job = Jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="job not found"
        )
    return job
