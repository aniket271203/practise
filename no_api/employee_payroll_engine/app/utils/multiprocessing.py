from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

def chunk_lists(items,n_workers=cpu_count()):
    size=(len(items)+n_workers-1)//n_workers
    return [items[i:i+size] for i in range(0,len(items),size)]

def run_parallel(worker_fn,chunks):
    with ProcessPoolExecutor(max_workers=cpu_count()) as pool:
        results=pool.map(worker_fn,chunks)
        
    return list(results)
