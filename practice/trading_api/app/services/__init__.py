from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from apis.trading_api.app.repositories import trade_repository
from apis.trading_api.app.schemas import TradeCreate, TradeStatus
from apis.trading_api.app.models import Trade
from typing import Optional, List
from apis.trading_api.app.logger import setup_logger

logger=setup_logger(__name__)

class TradeService:
    async def create_trade(self,db:AsyncSession,trade_data: TradeCreate)->Trade:
        logger.info(f"Creating Trade| symbol= {trade_data.symbol}, qty={trade_data.quantity}, price={trade_data.price}")
        trade=await trade_repository.create(db,trade_data)
        logger.info(f"Trade created Successfully | id={trade.id}")
        return trade 
    
    async def get_trade(self, db: AsyncSession, trade_id: int)->Optional[Trade]:
        logger.debug(f"fetching trade | id={trade_id}")
        trade=await trade_repository.get_by_id(db,trade_id)
        if not trade:
            logger.warning(f"trade does not exist | id={trade_id}")
            raise HTTPException(status_code=404, detail="trade_id does nto exist")
        logger.debug(f"fetching trade successful | id={trade_id}")
        return trade

    async def get_all_trades(self, db: AsyncSession,skip:int=0,limit:int=10)->Optional[Trade]:
        logger.debug(f"fetching all trades")
        trades=await trade_repository.get_all(db,skip=skip,limit=limit)
        logger.debug(f"found {len(trades)} trades")
        return trades
    
    async def get_trade_by_symbol(self,db: AsyncSession, symbol:str)->Optional[Trade]:
        logger.debug(f"fetching trades | symbol={symbol}")
        trades=await trade_repository.get_by_symbol(db,symbol)
        if not trades:
            logger.warning(f"trades not found | symbol={symbol}")
            raise HTTPException(status_code=404, detail="no trades for {symbol} exist")
        logger.debug(f"fetching trades successful | symbol={symbol}")
        return trades

    async def cancel_trade(self,db:AsyncSession,trade_id: int)->Trade:
        logger.info(f"Cancelling Trade | id={trade_id}")
        trade=await self.get_trade(db,trade_id)   # thsi will reuse the get trade and handle the trade does not exist automatically 
        if trade.status==TradeStatus.CANCELLED:
            logger.warning(f"trade already cancelled | id={trade_id}")
            raise HTTPException(status_code=400, detail="Trade already cancelled")
        if trade.status==TradeStatus.FILLED:
            logger.warning(f"filled trade cannot be cancelled | id={trade_id}")
            raise HTTPException(status_code=400, detail="cannot cancel a filled trade")
        trade=await trade_repository.update_status(db,trade,TradeStatus.CANCELLED)
        logger.info(f"Trade successfully Cancelled | id={trade_id}")
        return trade
    
trade_service=TradeService()