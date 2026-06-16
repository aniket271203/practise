from apis.trader_api.app.models import Position
from apis.trader_api.app.schemas import PositionCreate
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List,Optional
from apis.trader_api.app.repositories.position import position_repository
from apis.trader_api.app.logger import setup_logger
from fastapi import HTTPException

logger=setup_logger(__name__)

class PositionServices:
    
    async def get_by_symbol(self,db:AsyncSession,symbol:str)->List[Position]:
        logger.debug(f"fetching all Position by symbol | symbol={symbol}")
        position=await position_repository.get_by_symbol(db,symbol)  
        if not position:
                raise HTTPException(
                    status_code=404,
                    detail="Position does not Exist"
                )
        return position 
    
    async def get_by_trader_id(self,db:AsyncSession, id)->List[Position]:
        logger.debug(f"fetching position by trader_id | id={id}")
        position=await position_repository.get_by_trader_id(db,id)
        
        if not position:
            raise HTTPException(
                status_code=404,
                detail="Position does not Exist"
            )
        return position
    
    async def get_by_id(self,db:AsyncSession, id)->Position:
        logger.debug(f"fetching position by trader_id | id={id}")
        position=await position_repository.get_by_id(db,id)
        
        if not position:
            raise HTTPException(
                status_code=404,
                detail="Position does not Exist"
            )
        return position
    
position_services=PositionServices()