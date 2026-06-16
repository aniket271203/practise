from sqlalchemy.ext.asyncio import AsyncSession
from apis.trading_practise_api.app.models import Trade, Trader
from apis.trading_practise_api.app.schemas import TradeCreate, TraderCreate, TradeStatus, TradeSide, TradeExchange
from apis.trading_practise_api.app.logger import setup_logger
from typing import List, Optional
from sqlalchemy.exc import OperationalError
from apis.trading_practise_api.app.utils import retry 
from sqlalchemy import select

logger=setup_logger(__name__)

class TraderRepository:
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def create_trader(self,db:AsyncSession, trader_data:TraderCreate)->Trader:
        new_trader=Trader(
            name=trader_data.name,
            email=trader_data.email,
            desk=trader_data.desk,
            is_active=True
        )
        db.add(new_trader)
        await db.commit()
        await db.refresh(new_trader)
        logger.info("created new Trader in DB")
        return new_trader
    
    async def get_all(self, db:AsyncSession,)->Optional[Trader]:
        query=select(Trader)
        result=await db.execute(query.filter(Trader.is_active==True))
        return result.scalars().all()
    
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def get_by_id(self,db:AsyncSession,trader_id:int)->Trader:
        result=await db.execute(select(Trader).filter(Trader.id==trader_id))
        return result.scalar_one_or_none()
    
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def delete_trader(self,db:AsyncSession,trader:Trader)->Trader:
        trader.is_active=False
        await db.commit()
        await db.refresh(trader)
        return trader
    
trader_repository=TraderRepository()
        