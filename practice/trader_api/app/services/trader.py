from apis.trader_api.app.models import Trader
from apis.trader_api.app.schemas import TraderCreate,TraderSummary
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from apis.trader_api.app.repositories.trader import trader_repository
from apis.trader_api.app.logger import setup_logger
from fastapi import HTTPException

logger=setup_logger(__name__)

class TraderServices:
    async def create_trader(self,db:AsyncSession,trader_data:TraderCreate)->Trader:
        logger.info("creating a new trader")
        trader=await trader_repository.create(db,trader_data)
        logger.info(f"Created Trader Successfully | id={trader.id}")
        return trader
    
    async def get_all(self,db:AsyncSession)->List[Trader]:
        logger.debug("fetching all traders")
        return await trader_repository.get_all(db)    
    
    async def get_by_id(self,db:AsyncSession, trader_id)->Trader:
        logger.debug(f"fetching trader | id={trader_id}")
        trader=await trader_repository.get_by_id(db,trader_id)
        
        if not trader:
            raise HTTPException(
                status_code=404,
                detail="Trader does not Exist"
            )
        return trader
    
    async def get_summary(self,db:AsyncSession,id:int)->TraderSummary:
        trader=await self.get_by_id(db,id)
        return await trader_repository.get_summary(db,trader)
    
trader_services=TraderServices()