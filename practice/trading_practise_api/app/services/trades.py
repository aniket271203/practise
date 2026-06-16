from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from apis.trading_practise_api.app.logger import setup_logger
from apis.trading_practise_api.app.repositories.trade_repository import trade_repository
from apis.trading_practise_api.app.repositories.trader_repository import trader_repository
from apis.trading_practise_api.app.models import Trade, Trader
from apis.trading_practise_api.app.schemas import TradeCreate, TradeStatus
from typing import Optional, List

logger = setup_logger(__name__)


class TradeServices:
    async def create_trade(self, db: AsyncSession, trade_data: TradeCreate) -> Trade:
        logger.info("Creating Trade")
        trader=await trader_repository.get_by_id(db,trade_data.trader_id)
        if not trader:
            logger.warning("trader does not exist")
            raise HTTPException(
                status_code=400,
                detail=f"trader with id={trade_data.trader_id} does not exist"
            )
        if not trader.is_active:
            logger.warning("Trader is not active")
            raise HTTPException(
                status_code=400,
                detail=f"Trader with id={trade_data.trader_id} is not active"
            )
        trade = await trade_repository.create_trade(db, trade_data=trade_data)
        logger.info(f"Created a trade | id={trade.id}")
        return trade

    async def get_all(self, db: AsyncSession)->Optional[Trade]:
        logger.debug("fetching Trades")
        return await trade_repository.get_all(db)

    async def get_trade_by_id(self, db: AsyncSession, trade_id:int)->Trade:
        logger.debug(f"fetching Trade | id={trade_id}")
        trade=await trade_repository.get_by_id(db,trade_id)
        if not trade:
            logger.warning("trade does not exit")
            raise HTTPException(
                status_code=404,
                detail=f"trade does nopt exist | id={trade_id}"
            )
        return trade

    async def update_status(self,db:AsyncSession,trade_id:int,status:TradeStatus)->Trade:
        logger.info(f"Updating status | to={status} id={trade_id}")
        trade=await self.get_trade_by_id(db,trade_id)
        if status==TradeStatus.FILLED:
            if trade.status==TradeStatus.CANCELLED:
                logger.warning("cannot fill cancelled trade")
                raise HTTPException(
                    status_code=400,
                    detail="Cannot Fill Cancelled trade"
                )
            if trade.status==TradeStatus.FILLED:
                logger.warning("Trade Already Filled")
                raise HTTPException(
                    status_code=400,
                    detail="Trade already filled"
                )
        if status==TradeStatus.CANCELLED:
            if trade.status==TradeStatus.CANCELLED:
                logger.warning("trade already Cancelled")
                raise HTTPException(
                    status_code=400,
                    detail="trade already cancelled"
                )
            if trade.status==TradeStatus.FILLED:
                logger.warning("filled trade cannot be cancelled")
                raise HTTPException(
                    status_code=400,
                    detail="dilled trade cannot be cancelled"
                )
        trade=await trade_repository.update_status(db,trade,status)
        return trade
        
    async def get_trader(self,db:AsyncSession,trader_id:int)->Trader:
        logger.debug("fetching Trader")
        trader=await trade_repository.get_trader(db,trader_id)
        return trader
    
trade_services=TradeServices()