from apis.trading_api.app.models import Trade
from apis.trading_api.app.schemas import TradeCreate, TradeStatus
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apis.trading_api.app.logger import setup_logger
from apis.trading_api.app.utils import retry
from sqlalchemy.exc import OperationalError

logger=setup_logger(__name__)

class TradeRepository:
    @retry(max_attempts=3,delay=0.5,exceptions=(OperationalError,))
    async def create(self, db: AsyncSession, trade: TradeCreate) -> Trade:
        new_trade = Trade(
            symbol=trade.symbol,
            quantity=trade.quantity,
            price=trade.price,
            status=TradeStatus.PENDING
        )
        db.add(new_trade)
        await db.commit()
        await db.refresh(new_trade)
        logger.info(f"Created a new trade in the DB | id={new_trade.id}")
        return new_trade

    async def get_all(self, db: AsyncSession,skip:int=0,limit:int=10) -> Optional[Trade]:
        result= await db.execute(select(Trade).offset(skip).limit(limit))
        return result.scalars().all()

    @retry(max_attempts=3, delay=0.5, exceptions=(OperationalError,))
    async def get_by_id(self, db: AsyncSession, trade_id: int) -> Optional[Trade]:
        result= await db.execute(select(Trade).filter(Trade.id == trade_id))
        return result.scalar_one_or_none()

    async def get_by_symbol(self, db: AsyncSession, symbol: str) -> Optional[Trade]:
        result= await db.execute(select(Trade).filter(Trade.symbol==symbol.upper()))
        return result.scalars().all()
    
    @retry(max_attempts=3, delay=0.5, exceptions=(OperationalError,))
    async def update_status(self,db: AsyncSession,trade:Trade, status: TradeStatus) -> Trade:
        trade.status=status
        await db.commit()
        await db.refresh(trade)
        return trade
    
trade_repository=TradeRepository()