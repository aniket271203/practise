
from concurrent.futures import ProcessPoolExecutor
from sqlalchemy.orm import DeclarativeBase
from random import randint
import csv
import math
from multiprocessing import cpu_count
import sqlite3
from fastapi import FastAPI, HTTPException, BackgroundTasks
import uuid


Jobs = {}


class Trade(DeclarativeBase):
    id: int
    symbol: str
    quantity: int
    price: float


def random_factor():
    return randint(0, 1)


def calculate_risk(price: float, quantity: int):
    return (
        quantity *
        price *
        random_factor()
    )


def process_chunk(rows):
    results = []
    for row in rows:
        id, symbol, quantity, price = row
        risk_score = calculate_risk(float(price), int(quantity))
        results.append((int(id), symbol, int(
            quantity), float(price), risk_score))

    return results


def chunk_lists(items, n_worker):
    size = (len(items)+n_worker-1)//n_worker
    return [items[i:i+size] for i in range(0, len(items), size)]


def read_csv(csv_file: str, chunk_size: int = 10000):
    with open(csv_file, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


def read_db(db_table: str, chunk_size: int = 100000):
    db = sqlite3.connect(db_table)
    last_id = 0
    while True:
        cur = db.execute(f"""
                         SELECT * 
                         FROM trades 
                         WHERE id>? 
                         ORDER BY id 
                         LIMIT ?
                         """,
                         (last_id, chunk_size)).fetchall()

        if not cur:
            break
        last_id = cur[-1][0]
        yield cur

    db.close()


def run_ingest(csv_file: str, db_table: str, job_id: str):
    try:
        if csv_file:
            db = sqlite3.connect('trades.db')
            with ProcessPoolExecutor(max_workers=cpu_count()) as pool:
                for rows in read_csv(csv_file):
                    chunks=chunk_lists(rows,cpu_count())
                    
                    results=pool.map(process_chunk,chunks)
                    
                    for chunk_result in results:
                        db.execute("""CREATE TABLE IF NOT EXISTS new_table(
                                id INTEGER PRIMARY KEY,
                                symbol TEXT,
                                quantity INTEGER,
                                price REAL,
                                risk_score REAL
                                )
                                """)
                        db.executemany(f"INSERT INTO new_table VALUES(?,?,?,?,?)", chunk_result)

                db.commit()
            db.close()
        Jobs[job_id] = {"status": "completed"}
    except Exception as e:
        Jobs[job_id]={"status":"failed", "errors":e}


app = FastAPI()


@app.post('/run_ingest/{file}', status_code=202)
async def ingestion(file: str, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    Jobs[job_id] = {"status": "running"}
    bg.add_task(run_ingest, file, None, job_id)
    return Jobs[job_id]
