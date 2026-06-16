from fastapi import HTTPException
from apis.trading_practise_api.app.logger import setup_logger
from apis.trading_practise_api.app.repositories.trader_repository import trader_repository
from sqlalchemy.ext.asyncio import AsyncSession
from apis.trading_practise_api.app.schemas import TraderCreate
from apis.trading_practise_api.app.models import Trader
from typing import List, Optional

logger = setup_logger(__name__)


class TraderServices:
    async def create_trader(self, db: AsyncSession, trader_data: TraderCreate) -> Trader:
        logger.info("Creating a Trader")
        trader = await trader_repository.create_trader(db, trader_data)
        logger.info(f"sucessfully created trader | id={trader.id}")
        return trader

    async def get_all(self, db: AsyncSession) -> Optional[Trader]:
        logger.debug("fetching all traders")
        return await trader_repository.get_all(db)

    async def get_trader_by_id(self, db: AsyncSession, trader_id: int) -> Trader:
        logger.debug(f"fetching trader| id={trader_id}")
        trader = await trader_repository.get_by_id(db, trader_id)
        if not trader:
            logger.warning("trader deos not exist")
            raise HTTPException(
                status_code=404,
                detail=f"Trader does not exist | id={trader_id}"
            )
        return trader

    async def delete_trader(self, db: AsyncSession, trader_id: int) -> Trader:
        logger.info(f"deleting Trader | id={trader_id}")
        trader = await self.get_trader_by_id(db, trader_id)
        if not trader.is_active:
            logger.warning("trader already deleted")
            raise HTTPException(
                status_code=400,
                detail="trader already deleted"
            )
        trader=await trader_repository.delete_trader(db, trader)
        return trader


trader_services = TraderServices()
