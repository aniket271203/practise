from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Coupon
from app.schemas import CouponCreate
from app.repositories.coupon import coupon_repository
from typing import List
from app.utils.multiprocessing import run_parallel, chunk_list
from random import random
from datetime import datetime,timezone


class CouponService:
    async def create_coupon(self,db:AsyncSession,coupon_data:CouponCreate)->Coupon:
        coupon= await coupon_repository.create(db,coupon_data)
        return coupon
    
    async def get_by_id(self,db:AsyncSession,coupon_id:int)->Coupon:
        coupon=await coupon_repository.get_by_id(db,coupon_id)
        if not coupon:
            raise ValueError("status_code=404, detail=Coupon Not Found")
        return coupon
    
    async def get_by_code(self,db:AsyncSession,coupon_code:str)->Coupon:
        coupon=await coupon_repository.get_by_code(db,coupon_code=coupon_code)
        if not coupon:
            raise ValueError("status_code=404, detail=Coupon Not Found")
        return coupon
    
    async def get_top_coupons(self,db:AsyncSession)->List[Coupon]:
        coupons=await coupon_repository.get_top_coupons(db)
        
        return coupons
    
    def process_chunk(rows):
        results=[]
        for row in rows:
            fraud_score=row.discount_percent*random(0,1)
            processed_at=datetime.now(timezone.utc)
            results.append({"id":int(row.id),"fraud_score":fraud_score,"processed_at":processed_at})
        
        return results
            
    
    async def fraud_calculate(self,db:AsyncSession):
        last_id=0
        chunk_size=10000
        while True:
            db_chunk=await coupon_repository.read_db_chunk(db,last_id,chunk_size)
            if not db_chunk:
                break
            
            chunks=chunk_list(db_chunk)
            
            results=run_parallel(self.process_chunk,chunks)
            
            flattened=[]
            for res in results:
                flattened.extend(res)
                
            await coupon_repository.bulk_updates(db,flattened)
            last_id=db_chunk[-1].id
            
    
coupon_service=CouponService()