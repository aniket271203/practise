from sqlalchemy import select, func, sum, count, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case
from apis.trading_practise_api.app.models import Trade
from fastapi import HTTPException
from apis.trading_practise_api.app.models import Trader


class AnalyticsRepostory:
    async def get_system_summary(self, db: AsyncSession) -> dict:

        trade_result = await db.execute(
            select(
                func.count(Trade.id).label("total"),
                func.sum(
                    case((Trade.status == "filled", 1),
                         else_=0)
                ).label("filled"),
                func.sum(
                    case((Trade.status == "pending", 1),
                         else_=0)
                ).label("pending"),
                func.sum(
                    case((Trade.status == "cancelled", 1),
                         else_=0)
                ).label("cancelled"),
                func.sum(Trade.price*Trade.quantity
                         ).label("volume")
            )
        )

        trade_row = trade_result.first()

        trader_result = await db.execute(
            select(
                func.count(Trader.id).label("total"),
                func.sum(
                    case(Trader.is_active == True, 1),
                    else_=0
                ).label("active")
            )
        )

        trader_row = trader_result.first()

        return {
            "total_trades": trade_row.total or 0,
            "pending_trades": trade_row.pending or 0,
            "filled_trades": trade_row.filled or 0,
            "cancelled_trades": trade_row.cancelled or 0,
            "total_volume": float(trade_row.volume or 0),
            "total_traders": trader_row.total or 0,
            "active_traders": trader_row.active or 0
        }

    async def get_trader_summary(self,db: AsyncSession, trader_id: int) -> dict:

        trader_result = await db.execute(select(Trader).filter(Trader.id == trader_id))
        trader = trader_result.scalar_one_or_none()
        if not trader:
            raise HTTPException(
                status_code=404,
                detail=f"Trader does not exist | id={trader_id}"
            )

        stats_result = await db.execute(
            select(
                func.count(Trade.id).label("total"),
                func.sum(
                    case((Trade.status == "filled", 1),
                         else_=0)
                ).label('filled'),
                func.sum(
                    case((Trade.status == "pending", 1),
                         else_=0)
                ).label('pending'),
                func.sum(
                    case((Trade.status == "cancelled", 1),
                         else_=0)
                ).label('cancelled'),
                func.sum(Trade.price*Trade.quantity).label('volume'),
            ).filter(Trade.trader_id==trader_id)
        )

        stats = stats_result.first()

        symbol_result = await db.execute(
            select(Trade.symbol,
                   func.count(Trade.id).label('trade_count'))
            .filter(Trade.trader_id == trader_id)
            .group_by(Trade.symbol)
            .order_by(desc("trade_count"))
            .limit(1)
        )
        symbol_row = symbol_result.first()

        return {
            "trader_id": trader_id,
            "trader_name": trader.name,
            "desk": trader.desk,
            "total_trades": stats.total or 0,
            "filled_trades": stats.filled or 0,
            "cancelled_trades": stats.cancelled or 0,
            "pending_trades": stats.pending or 0,
            "total_volume": float(stats.volume or 0),
            "most_traded_symbol": symbol_row.symbol if symbol_row else None
        }
