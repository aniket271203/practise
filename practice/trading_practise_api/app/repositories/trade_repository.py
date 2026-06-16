from sqlalchemy.ext.asyncio import AsyncSession
from apis.trading_practise_api.app.models import Trade, Trader
from apis.trading_practise_api.app.schemas import TradeCreate, TraderCreate, TradeStatus, TradeSide, TradeExchange
from apis.trading_practise_api.app.logger import setup_logger
from typing import List, Optional
from sqlalchemy.exc import OperationalError
from apis.trading_practise_api.app.utils import retry 
from sqlalchemy import select

logger=setup_logger(__name__)

class TradeRepository:
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def create_trade(self,db:AsyncSession, trade_data:TradeCreate)->Trade:
        new_trade=Trade(
            symbol=trade_data.symbol,
            quantity=trade_data.quantity,
            price=trade_data.price,
            side=trade_data.side,
            exchange=trade_data.exchange,
            status=TradeStatus.PENDING,
            trader_id=trade_data.trader_id
        )
        db.add(new_trade)
        await db.commit()
        await db.refresh(new_trade)
        logger.info("created new Trade in DB")
        return new_trade
    
    async def get_all(self, db:AsyncSession, skip:int=0, limit:int=10,symbol:str=None,status:TradeStatus=None,side:TradeSide=None,exchange:TradeExchange=None, trader_id:int=None)->Optional[Trade]:
        query=select(Trade)
        if symbol:
            query=query.filter(Trade.symbol==symbol)
        if status:
            query=query.filter(Trade.status==status)
        if side:
            query=query.filter(Trade.side==side)
        if exchange:
            query=query.filter(Trade.exchange==exchange)
        if trader_id:
            query=query.filter(Trade.trader_id==trader_id)
        result=await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def get_by_id(self,db:AsyncSession,trade_id:int)->Trade:
        result=await db.execute(select(Trade).filter(Trade.id==trade_id))
        return result.scalar_one_or_none()
    
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def get_trader(self,db:AsyncSession,trader_id:int)->List[Trade]:
        result=await db.execute(select(Trade).where(Trade.trader_id==trader_id))
        return result.scalars().all()
    
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def update_status(self,db:AsyncSession,trade:Trade, status:TradeStatus)->Trade:
        trade.status=status
        await db.commit()
        await db.refresh(trade)
        return trade
    
trade_repository=TradeRepository()
        