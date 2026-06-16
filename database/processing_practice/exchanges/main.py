# internal_expected.csv — 60 trades (your ground truth)
# exchange_a.csv (24 rows) — columns: trade_ref, ticker, qty, px, direction, exec_time, exec_status
# exchange_b.csv (13 rows) — columns: id, sym, side, price, quantity, time, state (note: space-separated timestamp, not ISO)
# exchange_c.csv (21 rows) — columns: orderId, instrument, action, fillQty, fillPrice, ts, status (note: lowercase side values)
from enum import Enum
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import csv
import aiosqlite
import sqlite3

process_executer = ProcessPoolExecutor(max_workers=cpu_count())


class OrderStatus(str, Enum):
    FILLED = "filled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def internal_expected_row(exchange: str, trade_id: int, symbol: str, side: str, price: float, quantity: int, timestamp, status: str):
    if status == "complete" or status == "EXECUTED" or status == "DONE":
        status = OrderStatus.COMPLETED
    elif status == "running" or status == "EXECUTING" or status == "DOING":
        status = OrderStatus.FILLED
    elif status == "cancelled" or status == "REJECTED" or status == "CANCEL":
        status = OrderStatus.CANCELLED
    return (trade_id, exchange, symbol.upper(), side.upper(), price, quantity, timestamp, status)


def parser_a(rows):
    results = []
    for row in rows:
        trade_ref, ticker, qty, px, direction, exec_time, exec_status = row
        updated_row = internal_expected_row(exchange="A", trade_id=int(trade_ref), symbol=ticker, price=float(
            px), timestamp=exec_time, status=exec_status, quantity=int(qty), side=direction)
        results.append(updated_row)
    return results


def parser_b(rows):
    results = []
    for row in rows:
        id, sym, side, price, quantity, time, state = row
        updated_row = internal_expected_row(exchange="B", trade_id=int(id), symbol=sym, price=float(
            price), timestamp=time, status=state, quantity=int(quantity), side=side)
        results.append(updated_row)
    return results


def parser_c(rows):
    results = []
    for row in rows:
        orderId, instrument, action, fillQty, fillPrice, ts, status = row
        updated_row = internal_expected_row(exchange="C", trade_id=int(orderId), symbol=instrument, price=float(
            fillPrice), timestamp=ts, status=status, quantity=int(fillQty), side=action)
        results.append(updated_row)

    return results


def parser_internal(rows):
    results = []
    for row in rows:
        trade_id, exchange, symbol, price, qty, side, timestamp = row
        results.append((int(trade_id), exchange, symbol.upper(),
                       side.upper(), float(price), int(qty), timestamp))
    return results


def chunk_list(rows, n_workers):
    size = (len(rows)+n_workers-1)//n_workers
    return [rows[i:i+size] for i in range(0, len(rows), size)]


def run_ingest():
    with open("exchange_a.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows_a = list(reader)

    with open("exchange_b.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows_b = list(reader)

    with open("exchange_c.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows_c = list(reader)

    chunks_a = chunk_list(rows_a, cpu_count())
    chunks_b = chunk_list(rows_b, cpu_count())
    chunks_c = chunk_list(rows_c, cpu_count())

    results_a = [process_executer.submit(
        parser_a, chunks) for chunks in chunks_a]

    results_b = [process_executer.submit(
        parser_b, chunks) for chunks in chunks_b]

    results_c = [process_executer.submit(
        parser_c, chunks) for chunks in chunks_c]

    row_results = []
    for result in as_completed(results_a):
        row_results.extend(result.result())
    for result in as_completed(results_b):
        row_results.extend(result.result())
    for result in as_completed(results_c):
        row_results.extend(result.result())

    db = sqlite3.connect('trades.db')
    db.execute("""
               CREATE TABLE IF NOT EXISTS external_trades (
               trade_id INTEGER PRIMARY KEY,
               exchange TEXT,
               symbol TEXT,
               side TEXT,
               price REAL,
               quantity INTEGER,
               timestamp DATETIME,
               status TEXT
               )
               """)
    db.executemany(
        "INSERT INTO external_trades VALUES(?,?,?,?,?,?,?,?)", row_results)
    db.commit()
    db.close()

    return


def compare_trades():
    with open("internal_expected.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

    row_results = parser_internal(rows)

    db = sqlite3.connect('trades.db')
    db.execute("""
               CREATE TABLE IF NOT EXISTS internal_trades (
               trade_id INTEGER PRIMARY KEY,
               exchange TEXT,
               symbol TEXT,
               side TEXT,
               price REAL,
               quantity INTEGER,
               timestamp DATETIME
               )
               """)
    db.executemany(
        "INSERT INTO internal_trades VALUES(?,?,?,?,?,?,?)", row_results)
    db.commit()
    db.close()

async def reconsilation_sql():
    async with aiosqlite.connect('trades.db') as db:
        rows=await db.execute("""
                SELECT * FROM
                internal_trades i LEFT JOIN external_trades e 
                ON e.trade_id=i.trade_id
                WHERE e.trade_id is NULL             
                """)
        results=await rows.fetchall()
        print(results)
    
    async with aiosqlite.connect('trades.db') as db:
        extra= await db.execute("""
                    SELECT * FROM
                    external_trades e LEFT JOIN
                    internal_trades i 
                    ON e.trade_id=i.trade_id
                    WHERE i.trade_id is NULL            
                                """)
        results=await extra.fetchall()
        print(results)
    
    async with aiosqlite.connect('trades.db') as db:
        mismatched=await db.execute("""
                    SELECT * FROM
                    external_trade e JOIN
                    internal_trade i
                    ON e.trade_id=i.trade_id
                    WHERE e.price!=i.price or e.quantity!=i.quantity              
                                    """)
    
        results=await mismatched.fetchall()
        print(results)