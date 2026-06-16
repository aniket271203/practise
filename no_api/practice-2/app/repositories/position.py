from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trader, Position, Trade
from sqlalchemy import select, update, func, case
from app.schemas import PositionCreate


class PositionRepository:
    async def create(self, db: AsyncSession, position_data: PositionCreate) -> Position:
        position = Position(
            trader_id=position_data.trader_id,
            symbol=position_data.symbol,
            quantity=position_data.quantity,
            average_price=position_data.average_price
        )
        db.add(position)
        await db.flush()

        return position
    
    async def get_all(self,db:AsyncSession):
        result=await db.execute(
            select(
                Position
            )
        )
        return result.scalars().all()

    async def get_for_update(self, db: AsyncSession, trader_id: int, symbol: str) -> Position:
        result = await db.execute(select(Position).where(Position.trader_id == trader_id).where(Position.symbol == symbol).with_for_update())

        return result.scalar_one_or_none()

    async def delete(self, db: AsyncSession, position: Position) -> Position:
        await db.delete(position)
        await db.flush()
        return position

    async def get_position_summary(self, db: AsyncSession, trader_id: int):
        result = await db.execute(select(
            func.count(Position.id).label("position_count"),
            func.sum(Position.quantity *
                     Position.average_price).label("portfolio_value")
        ).where(Position.trader_id == trader_id)
        )

        return result.first()

    async def read_db_chunk(self, db: AsyncSession, last_id: int, chunk_size: int):
        results = await db.execute(
            select(
                Position
            )
            .where(
                Position.id > last_id
            )
            .where(
                Position.processed_at.is_(None)
            )
            .order_by(
                Position.id
            )
            .limit(
                chunk_size
            )
        )

        return results.scalars().all()

    async def bulk_updates(self, db: AsyncSession, updates):
        await db.execute(
            update(
                Position
            ),
            updates
        )
        await db.commit()


position_repository = PositionRepository()
