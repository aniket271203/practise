import csv, math, sqlite3, time
from multiprocessing import Pool, cpu_count

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

def chunk_list(items, n_chunks):
    size = (len(items) + n_chunks - 1) // n_chunks
    return [items[i:i+size] for i in range(0, len(items), size)]

def ingest():
    # read each of the rows of the csv file 500K rows 
    with open("trades.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

    # now instead of executing all 500k rows at once that would take time we split it in chunks 
    # we need to first findout how many cpu we have using cpu_count()
    # then split the rows into chunks and get a list of chunks using the func()-> return rows[i:i+size] we need to find out what the size is using the len(rows + n_chunks-1)//n_chunks
    # and then run the loop with range(0,len(trades),size)
    n_workers = cpu_count()
    chunks = chunk_list(rows, n_workers)

    # once we have the chunks list ready we can distribute it across the processes using Pool() as pool: pool.map(worker,chunk_list)
    # and collect them in chunked_results
    with Pool(processes=n_workers) as pool:
        chunked_results = pool.map(process_chunk, chunks)
    
    # Then make sure your chunked results are put and combined into one single list 
    all_rows = [row for chunk in chunked_results for row in chunk]

    # then comes the fun part bulk update using sqlite3
    # make sure you know how to write the sql queries
    conn = sqlite3.connect("trades.db")
    conn.execute("""CREATE TABLE trades (
        trade_id INTEGER PRIMARY KEY, symbol TEXT, price REAL,
        qty INTEGER, side TEXT, timestamp TEXT, risk_score REAL)""")
    conn.executemany("INSERT INTO trades VALUES (?,?,?,?,?,?,?)", all_rows)
    conn.commit()
    conn.close()
    return len(all_rows)

if __name__ == "__main__":
    t0 = time.time()
    count = ingest()
    print(f"Processed {count} rows in {time.time()-t0:.2f}s")