from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from apis.portfolio_api.app.models import Position
from apis.portfolio_api.app.schemas import PositionCreate
from apis.portfolio_api.app.utils import retry
from sqlalchemy.sql import func
from sqlalchemy.exc import OperationalError
from sqlalchemy import select


class PositionRepository:
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError))
    async def create_position(self, db: AsyncSession, position: PositionCreate) -> Position:
        new_position = Position(
            symbol=position.symbol,
            quantity=position.quantity,
            avg_price=position.avg_price
        )
        db.add(new_position)
        await db.commit()
        await db.refresh(new_position)
        return new_position

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Position]:
        positions = await db.execute(select(Position).offset(skip).limit(limit))
        return positions.scalars().all()

    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError))
    async def get_by_id(self, db: AsyncSession, position_id: int) -> Optional[Position]:
        position=await db.execute(select(Position).filter(Position.id == position_id))
        return position.scalar_one_or_none()

    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError))
    async def get_by_symbol(self, db: AsyncSession, symbol: str) -> Optional[Position]:
        positions=await db.execute(select(Position).filter(Position.symbol == symbol))
        return positions.scalars().all()

    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError))
    async def update_position(self, position: Position, db: AsyncSession, quantity: int, avg_price: float) -> Position:
        position.avg_price = avg_price
        position.quantity = quantity
        await db.commit()
        await db.refresh(position)
        return position

    async def delete_position(self, db: AsyncSession, position: Position) -> Position:
        deleted_position = position
        await db.delete(position)
        await db.commit()
        return deleted_position

    async def get_total_value(self, db: AsyncSession):
        return await db.execute(select(func.sum(Position.quantity*Position.avg_price))).scalar()


position_repository = PositionRepository()
