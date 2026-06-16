from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trader, Position, Trade
from sqlalchemy import select, update, func, case
from sqlalchemy.orm import selectinload
from app.schemas import TraderCreate


class TraderRepository:
    async def create(self, db: AsyncSession, trader_data: TraderCreate)->Trader:
        trader=Trader(
            name=trader_data.name,
            cash_balance=trader_data.cash_balance
        )
        db.add(trader)
        await db.flush()
        
        return trader
    
    async def get_all(self,db:AsyncSession):
        result= await db.execute(
            select(
                Trader
            )
        )
        return result.scalars().all()
    
    async def get_for_update(self, db: AsyncSession, trader_id: int) -> Trader:
        result = await db.execute(select(Trader).where(Trader.id == trader_id).with_for_update())

        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, trader_id: int) -> Trader:
        result = await db.execute(select(Trader).where(Trader.id == trader_id))

        return result.scalar_one_or_none()

    async def get_top_traders(self, db: AsyncSession):

        portfolio_value = func.coalesce(
            func.sum(Position.quantity*Position.average_price), 0).label('portfolio_value')

        result = await db.execute(select(Trader.id,
                                         Trader.name,
                                         portfolio_value)
                                  .select_from(Trader)
                                  .join(Position, Trader.id == Position.trader_id)
                                  .group_by(Trader.id, Trader.name)
                                  .order_by(portfolio_value.desc())
                                  .limit(5)
                                  )
        return result.all()

    async def get_traders_above_average_portfolio(self, db: AsyncSession):
        portfolio_value = (
            func.coalesce(
                func.sum(
                    Position.quantity*Position.average_price
                ),
                0
            ).label('portfolio_value')
        )

        portfolio_values = (
            select(
                Position.trader_id.label('trader_id'),
                portfolio_value
            )
            .group_by(Position.trader_id)
            .cte('portfolio_values')
        )

        average_portfolio = (
            select(
                func.avg(portfolio_values.c.portfolio_value))
            .scalar_subquery()
        )

        result = await db.execute(
            select(
                Trader.id,
                Trader.name,
                portfolio_values.c.portfolio_value
            )
            .select_from(Trader)
            .join(
                portfolio_values,
                portfolio_values.c.trader_id == Trader.id
            )
            .where(
                portfolio_values.c.portfolio_value > average_portfolio
            )
        )
        return result.all()

    async def get_trader_positions(self, db: AsyncSession, trader_id: int):
        result = await db.execute(
            select(
                Trader
            )
            .options(
                selectinload(
                    Trader.positions
                )
            )
            .where(
                Trader.id == trader_id
            )
        )

        return result.scalar_one_or_none()


trader_repository = TraderRepository()
