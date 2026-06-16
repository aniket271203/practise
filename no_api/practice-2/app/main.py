from app.database import Base, engine, AsyncLocalSession
import asyncio
from app.schemas import TradeCreate,TraderCreate,PositionCreate
from app.services.trade import trade_service
from app.services.trader import trader_service
from app.services.position import position_service

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
async def main():
    await create_tables()
    
    async with AsyncLocalSession() as db:
        # await trader_service.create_trader(db,TraderCreate(name="anushka",cash_balance=300.0))
        # await trade_service.buy_trade(db,TradeCreate(trader_id=2,symbol="GOOG",quantity=4,price=10.0))
        # traders=await trader_service.get_traders_above_average_portfolio(db)
        # trades=await trade_service.get_symbols_above_average_volume(db)
        # print(traders)
        
        # print(trades)
        await position_service.process_risk(db)
        positions=await position_service.get_positions(db)
        print(positions)
        
if __name__=="__main__":
    asyncio.run(main())