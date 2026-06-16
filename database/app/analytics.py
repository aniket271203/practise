from sqlalchemy import select,case,func
from database.app.models import Trade


async def get_portfolio_summary(db):
    stats_results=await db.execute(
        select(
            func.count(Trade.id).label("total_trades"),
            func.sum(Trade.quantity*Trade.price).label("total_volume")
        )
    )   
    stats=stats_results.first()    
    
    symbols= await db.execute(
        select(
            Trade.symbol.label('symbol'),
            func.sum(Trade.quantity*Trade.price).label('volume')
        ).group_by(Trade.symbol)
    )
    
    symbols=symbols.scalars().all()
    
    return {
        "total_trades":stats.total_trades,
        "total_volume":stats.total_volume,
        "symbols":symbols
    }
    

from multiprocessing import Pool

def worker(chunk):
    total_value=0
    for item in chunk:
        total_value+=(item['price']*item['qty'])
        
    return total_value

CHUNK_SIZE=200000

def get_chunks(trades):
    for i in range(0, len(trades), CHUNK_SIZE):
        yield trades[i:i + CHUNK_SIZE]

trade=[]

with Pool(5) as p:
    results = p.map(worker, get_chunks(trade))
    
grand_total=sum(results)
print(grand_total)


skip=0
def process_trades(db):
    
    global skip
    count=db.execute(select(func.count(Trade.id))).scalar_one_or_none()
    
    
    with Pool(5) as p:
        chunk=db.execute(
            select(Trade).offset(skip).limit(CHUNK_SIZE)
        )
        skip+=CHUNK_SIZE
        result=p.map(worker,chunk)    
    
    grand_total=sum(result)
    return grand_total
    