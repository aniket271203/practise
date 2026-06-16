from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from apis.trader_api.app.utils import retry
from apis.trader_api.app.logger import setup_logger
from apis.trader_api.app.models import Trade
from apis.trader_api.app.schemas import TradeCreate, TradeSide
from typing import List

class TradeRepository:
    async def create(self,db:AsyncSession,trade_data:TradeCreate,side:TradeSide)->Trade:
        trade=Trade(
            trader_id=trade_data.trader_id,
            symbol=trade_data.symbol,
            quantity=trade_data.quantity,
            price=trade_data.price,
            side=side
        )
        db.add(trade)
        await db.flush()
        await db.refresh(trade)
        
        return trade
    
    async def get_by_id(self,db:AsyncSession,trade_id:int)->Trade:
        trade=await db.execute(select(Trade).filter(Trade.id==trade_id))
        return trade.scalar_one_or_none()
    
    async def get_all(self, db:AsyncSession,symbol:str=None,trader_id:int=None,side:TradeSide=None)->List[Trade]:
        query=select(Trade)
        if symbol:
            query=query.filter(Trade.symbol==symbol)
        if trader_id:
            query=query.filter(Trade.trader_id==trader_id)
        if side:
            query=query.filter(Trade.side==side)
        trades=await db.execute(query)
        return trades.scalars().all()
    
    
trade_repository=TradeRepository()