from apis.portfolio_api.app.repositories import position_repository
from apis.portfolio_api.app.schemas import PositionCreate
from sqlalchemy.ext.asyncio import AsyncSession
from apis.portfolio_api.app.models import Position
from typing import List, Optional
from fastapi import HTTPException
from apis.portfolio_api.app.logger import setup_logger

logger=setup_logger(__name__)

class PositionService:
    async def create_position(self, db: AsyncSession, position_data: PositionCreate) -> Position:
        logger.info(f"Creating Position | Symbol={position_data.symbol}")
        position=await position_repository.create_position(db, position_data)
        logger.info(f"created position Succesfully| symbol={position.symbol} id={position.id}")
        return position

    async def get_all_positions(self, db: AsyncSession) -> List[Position]:
        logger.debug("Fetching all Positions")
        positions = await position_repository.get_all(db)
        return positions

    async def get_position_by_id(self, db: AsyncSession, position_id: int) -> Position:
        logger.debug(f"fetching Position| id={position_id}")
        position = await position_repository.get_by_id(db, position_id)
        if not position:
            logger.warning(f"No positions found for id={position_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No position Found for id={position_id}"
            )
        return position

    async def get_position_by_symbol(self, db: AsyncSession, symbol: str) -> Optional[Position]:
        logger.debug(f"fetching Position| symbol={symbol}")
        positions = await position_repository.get_by_symbol(db, symbol)
        if not positions:
            logger.warning(f"No positions found for symbol={symbol}")
            raise HTTPException(
                status_code=404,
                detail=f"No position Found for symbol={symbol}"
            )
        return positions

    async def update_position(self, db: AsyncSession, id: int, quantity: int, avg_price: float) -> Position:
        logger.info(f"Updating position| id={id}")
        position = await self.get_position_by_id(db, id)
        if quantity <= 0:
            logger.warning(f"Invalid input quantity must be positive")
            raise HTTPException(
                status_code=400,
                detail="Invalid input quantity must be positive"
            )
        if avg_price <= 0:
            logger.warning(f"Invalid input price must be positive")
            raise HTTPException(
                status_code=400,
                detail="Invalid input price must be positive"
            )
        return await position_repository.update_position(position, db, quantity, avg_price)

    async def delete_position(self, db: AsyncSession, id: int):
        logger.info(f"Deleting Position from DB | id={id}")
        position = await self.get_position_by_id(db, id)
        deleted=await position_repository.delete_position(db, position)
        logger.info(f"Successfully Deleted Position from DB | id={id}")
        return deleted

    async def get_total_portfolio_value(self, db: AsyncSession):
        logger.debug("fetching total value for Positions")
        return await position_repository.get_total_value(db)


portfolio_services = PositionService()
