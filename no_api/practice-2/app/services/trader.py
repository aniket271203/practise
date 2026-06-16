from app.models import Position, Trade, Trader
from app.repositories.trade import trade_repository
from app.repositories.trader import trader_repository
from app.repositories.position import position_repository
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import TraderCreate
from typing import List

class TraderService:
    async def create_trader(self,db:AsyncSession,trader_data:TraderCreate)->Trader:
        async with db.begin():
            trader=await trader_repository.create(db,trader_data)
            return trader
        
    async def get_portfolio_summary(self, db: AsyncSession, trader_id: int):

        trader = await trader_repository.get_by_id(db, trader_id)

        position = await position_repository.get_position_summary(db, trader_id)
        return {
            "cash_balance": trader.cash_balance,
            "total_positions": position.position_count,
            "porfolio_value": position.portfolio_value
        }
    
    async def get_traders(self,db:AsyncSession)->List[Trader]:
        traders=await trader_repository.get_all(db)
        return traders

    async def get_top_traders(self, db: AsyncSession):
        traders = await trader_repository.get_top_traders(db)

        return traders

    async def get_traders_above_average_portfolio(self, db: AsyncSession):
        traders = await trader_repository.get_traders_above_average_portfolio(db)

        return traders

    async def get_trader_positions(self, db: AsyncSession, trader_id: int):
        trader = await trader_repository.get_trader_positions(db, trader_id)

        return {
            "trader_id": trader.id,
            "trader_name": trader.name,
            "positions": [
                {
                    "position_id": position.id,
                    "symbol": position.symbol,
                    "quantity": position.quantity,
                    "average_price": position.average_price
                }
                for position in trader.positions
            ]
        }


trader_service = TraderService()
