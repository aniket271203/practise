from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.risk import risk_repository
from app.utils.multiprocessing import run_parallel, chunk_lists
from random import randint
from datetime import datetime,timezone   

class RiskService:
    def process_chunk(self,rows):
        risk_factor=randint(0,1)
        results=[]
        for row in rows:
            risk_score=row.amount*risk_factor
            processed_at=datetime.now(timezone.utc).isoformat()
            results.append({"id":row.id,"risk_score":risk_score,"processed_at":processed_at})
        return results
        
    async def process_risk_scores(self,db: AsyncSession):
        # read payroll in chunks
        # use multiprocessing to calcute the risk scores 
        # compute the risk scores 
        # make bulk update
        risk_repository.set_up(db)
        chunk_size=10000
        last_id=0
        while True:
            chunk=await risk_repository.get_chunks(db,last_id,chunk_size)
            
            if not chunk:
                break
            chunks=chunk_lists(chunk)
            result=run_parallel(self.process_chunk,chunks)
            
            flattened=[]
            for chunk_result in result:
                flattened.extend(chunk_result)
                
            await risk_repository.bulk_updates(db,flattened)
            last_id=chunk[-1][0]
        


risk_service=RiskService()