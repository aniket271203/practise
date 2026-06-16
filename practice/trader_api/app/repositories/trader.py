from sqlalchemy import select,case
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from apis.trader_api.app.utils import retry
from apis.trader_api.app.schemas import TraderCreate, TraderSummary
from apis.trader_api.app.models import Trader,Position
from apis.trader_api.app.logger import setup_logger
from typing import List

logger=setup_logger(__name__)

class TraderRepositores:
    async def create(self,db:AsyncSession,trader_data:TraderCreate)->Trader:
        trader=Trader(
            name=trader_data.name,
            email=trader_data.email
        )
        db.add(trader)
        await db.commit()
        await db.refresh(trader)
        
        logger.info(f"Successfully Created a trader in DB | {trader.id}")
        return trader
    
    async def get_all(self,db:AsyncSession)->List[Trader]:
        traders=await db.execute(select(Trader))
        return traders.scalars().all()
    
    async def get_by_id(self,db:AsyncSession, trader_id:int)->Trader:
        trader=await db.execute(select(Trader).where(Trader.id==trader_id))
        return trader.scalar_one_or_none()
    
    async def get_summary(self,db:AsyncSession,trader:Trader)->TraderSummary:
        summary_stats=await db.execute(
            select(
                func.count(Position.id).label('total_positions'),
                func.sum(Position.quantity).label('total_trades'),
                func.sum(Position.quantity*Position.average_price).label("portfolio_value")
            ).where(Position.trader_id==trader.id)
        ) 
        summary=summary_stats.first()
        
        
        return {
            "trader_id":trader.id,
            "total_positions":summary.total_positions,
            "total_trades":summary.total_trades,
            "portfolio_value":summary.portfolio_value
                }
    
trader_repository=TraderRepositores()