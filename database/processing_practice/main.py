from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
import uuid
import sqlite3
import aiosqlite
import csv
import math
from fastapi import FastAPI, HTTPException, BackgroundTasks


process_executor = ProcessPoolExecutor(max_workers=cpu_count())

app = FastAPI()

Jobs = {}


@app.get('/analytics/vwap')
async def get_vwap():
    async with aiosqlite.connect("trades.db") as db:
        cur = await db.execute(
            """
            SELECT symbol,
            ROUND((SUM(price*qty))*1.0/SUM(qty),4) AS vwap
            FROM trades 
            GROUP BY symbol
            ORDER BY vwap DESC
            """
        )
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]

    return [dict(zip(cols, r)) for r in rows]


def chunk_list(items, n_workers):
    size = (len(items)+n_workers-1)//n_workers
    return [items[i:i+size] for i in range(0, len(items), size)]


def compute_risk_score(price: float, qty: int) -> float:
    notional = price * qty
    score = 0.0
    for i in range(1, 200):
        score += math.sin(notional / i) * math.log(i + 1)
    return round(score, 6)


def process_chunk(rows: list[tuple]) -> list[tuple]:
    """Runs in a WORKER process. Must be top-level (picklable)."""
    results = []
    for row in rows:
        trade_id, symbol, price, qty, side, ts = row
        price, qty = float(price), int(qty)
        risk = compute_risk_score(price, qty)
        results.append((int(trade_id), symbol, price, qty, side, ts, risk))
    return results


def run_ingest(job_id: str):
    with open("trades.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

    chunks = chunk_list(rows, cpu_count())

    chunk_results = process_executor.map(process_chunk, chunks)
    
    row_results=[r for chunk in chunk_results for r in chunk]
    
    conn=sqlite3.connect('trades.db')
    conn.executemany("INSERT INTO trades VALUES (?,?,?,?,?,?,?)",row_results)
    conn.commit()
    conn.close()
    Jobs[job_id]={"status":"Completed","rows":len(row_results)}

@app.post("/ingest",status_code=202)
async def start_ingestion(bg:BackgroundTasks):
    job_id=str(uuid.uuid4())
    Jobs[job_id]={"status":"running"}
    bg.add_task(run_ingest,job_id)
    return {"jon_id":job_id,"status":"running"}

@app.get("/ingest/{job_id}")
async def status(job_id:str):
    job=Jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404,
                            detail="job not found")
    return job
