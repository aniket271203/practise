from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trader, Position, Trade
from sqlalchemy import select, update, func, case
from app.schemas import TradeCreate, TradeSide


class TradeRepository:
    async def create(self, db: AsyncSession, trade_data: TradeCreate, side: TradeSide) -> Trade:
        trade = Trade(
            trader_id=trade_data.trader_id,
            symbol=trade_data.symbol,
            quantity=trade_data.quantity,
            price=trade_data.price,
            side=side
        )
        db.add(trade)
        await db.flush()

        return trade
    
    async def get_all(self,db:AsyncSession):
        result=await db.execute(
            select(
                Trade
            )
        )
        return result.scalars().all()

    async def get_symbols_above_average_volume(self, db: AsyncSession):
        symbols_table = (
            select(
                Trade.symbol,
                func.sum(Trade.quantity).label('volume')
            )
            .group_by(Trade.symbol)
            .cte('symbols_table')
        )

        avg_volume = (
            select(
                func.avg(symbols_table.c.volume)
            ).scalar_subquery()
        )

        result = await db.execute(
            select(
                symbols_table.c.symbol,
                symbols_table.c.volume
            )
            .where(symbols_table.c.volume > avg_volume)
        )

        return result.mappings().all()

    async def get_running_trade_value(self, db: AsyncSession):
        result = await db.execute(
            select(
                Trade.id.label('trade_id'),
                Trade.symbol.label('symbol'),
                (Trade.price*Trade.quantity).label('trade_value'),
                func.sum(Trade.price*Trade.quantity)
                .over(
                    partition_by=Trade.symbol,
                    order_by=Trade.created_at
                ).label('running_total')
            )
        )

        return result.mappings().all()


trade_repository = TradeRepository()
