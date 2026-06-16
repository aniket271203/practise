from apis.trader_api.app.models import Trade
from apis.trader_api.app.schemas import TradeCreate, TradeSide, PositionCreate
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from apis.trader_api.app.repositories.trade import trade_repository
from apis.trader_api.app.logger import setup_logger
from fastapi import HTTPException
from apis.trader_api.app.repositories.position import position_repository

logger = setup_logger(__name__)


class TradeServices:
    async def buy_trade(self, db: AsyncSession, trade_data: TradeCreate) -> Trade:
        async with db.begin():
            logger.info("creating a new trader")

            trade = await trade_repository.create(db, trade_data, TradeSide.BUY)

            pos = await position_repository.get_for_update(
                db, trade_data.trader_id,trade_data.symbol)

            if not pos:
                position_data = PositionCreate(
                    trader_id=trade_data.trader_id,
                    symbol=trade_data.symbol,
                    quantity=0,
                    average_price=0
                )
                await position_repository.create(db, position_data)

            position = await position_repository.get_for_update(
                db, trade_data.trader_id,trade_data.symbol)
            old_qty = position.quantity
            old_avg = position.average_price

            position.quantity += trade_data.quantity

            position.average_price = (
                (old_qty*old_avg)+(position.quantity*trade_data.price))/(old_qty+position.quantity)

            logger.info(f"Created Trader Successfully | id={trade.id}")
            return trade
    
    async def sell_trade(self, db: AsyncSession, trade_data: TradeCreate) -> Trade:
        async with db.begin():
            logger.info("creating a new trader")

            pos = await position_repository.get_for_update(
                db, trade_data.trader_id,trade_data.symbol)

            if not pos:
                raise HTTPException(
                    status_code=400,
                    detail="Position does not exist"
                )
            if trade_data.quantity>pos.quantity:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot sell more than available quantity"
                )
            
            pos.quantity -= trade_data.quantity

            trade = await trade_repository.create(db, trade_data, TradeSide.SELL)

            logger.info(f"Created Trader Successfully | id={trade.id}")
            return trade

    async def get_all(self, db: AsyncSession,symbol:str,trader_id:int,side:TradeSide) -> List[Trade]:
        logger.debug("fetching all traders")
        return await trade_repository.get_all(db,symbol,trader_id,side)

    async def get_by_id(self, db: AsyncSession, trade_id) -> Trade:
        logger.debug(f"fetching trade | id={trade_id}")
        trade = await trade_repository.get_by_id(db, trade_id)

        if not trade:
            raise HTTPException(
                status_code=404,
                detail="Trade does not Exist"
            )
        return trade


trade_services = TradeServices()
