from multiprocessing import cpu_count,Process,Queue
import time 

def producer(queue):
    
    for i in range(20):
        print(f"produced {i}")
        queue.put(i)
    
    for i in range(10):
        queue.put(None)
    
def process_chunk(chunk):
    return chunk*chunk

def consumer(queue,id):
    while True:
        chunk=queue.get()
        if not chunk:
            break
        
        print(f"Consumer id={id} processing Chunk_{chunk}")
        process_chunk(chunk)
        
        time.sleep(1)

def main():
    queue=Queue()
    
    p1=Process(target=producer,args=(queue,))
    
    
    consumers=[Process(target=consumer,args=(queue,i)) for i in range(10)]
    
    p1.start()
    for c in consumers:
        c.start()
        
    p1.join()
    for c in consumers:
        c.join()
        
        

if __name__=="__main__":
    start_time=time.perf_counter()
    
    main()
    print(time.perf_counter()-start_time)