# multiprocessing

## multiprocessing.Pool 
the workhorse that ias used for multi args function used to split the data into chunks and the map one thread to each of the chunk so they are processed in parallel
pool.map(), pool.apply_async, pool.startmap

## Process + Queue - 
for producer consumer problems,
Queue is the safe way to pass data between processes everything needs to be pickalable that is serializable

## concurrent.futures.ProcessPoolExecutor -
modern, cleaner API, often preferred in interviews because it composes nicely (as_completed, submit, exception propagation)

## Shared state: 
multiprocessing.Manager() for shared dicts/lists, or Value/Array for primitives — but interviewers love asking "why not just use a global variable" 
→ because each process gets a copy of memory, not a reference. Due to which nothing is shared by default between the processes and hence no case of Race condition but if we use a shared varaible through multiprocessing module then race conditions can occur

## The tradeoff conversation they'll want from you:

- asyncio → I/O-bound (API calls, DB queries, exchange websocket feeds)
- threading → I/O-bound with simpler shared-memory needs, limited by GIL for CPU work
- multiprocessing → CPU-bound (computing analytics over large datasets, batch processing)
- In a trading backend: ingesting/parsing exchange tick data files in parallel (multiprocessing) vs. handling concurrent API requests or exchange connections (asyncio).


2. SQL deep-dive — what's likely to be tested
Given "build SQL queries using backend," expect financial/time-series-flavored data (trades, orders, prices) and queries that test:

- Window functions: ROW_NUMBER(), RANK(), LAG/LEAD (e.g., "find the price change vs previous trade"), running totals with SUM() OVER (ORDER BY ... )
- Aggregations + GROUP BY with HAVING: e.g., "symbols with average trade volume > X"
- CTEs for breaking complex multi-step queries into readable pieces (this ties directly to "code cleanliness" they said they're judging)
- Joins: especially self-joins (matching buy/sell orders) and joins across orders/trades/instruments tables
- Date/time bucketing: grouping trades into time windows (1-min OHLC candles from tick data) — classic finance SQL exercise
- Indexing & EXPLAIN: be ready to explain why you'd index a column (e.g., symbol, timestamp) and how it affects query plans — ties to "performance tuning"



## Why each piece matters:

- process_chunk is module-level → required for pickling when sending to worker processes
- We chunk into N pieces (N = cpu_count) rather than pool.map(func, rows) directly → avoids 500K tiny IPC round-trips
- if __name__ == "__main__" → prevents infinite re-spawning on import in child processes
- DB write happens once, in the main process, after collecting all results → avoids SQLite concurrent-write issues