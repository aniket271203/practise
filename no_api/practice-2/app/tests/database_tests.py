import asyncio
from app.database import AsyncLocalSession
from app.schemas import TradeCreate,TraderCreate,PositionCreate
from app.services.trade import trade_service
from app.services.trader import trader_service
from app.services.position import position_service

async def create_trader_worker():
    async with AsyncLocalSession() as db:
        await trader_service.create_trader(db,TraderCreate(name="Aniket",cash_balance=300.0))


async def buy_trade_worker():
    async with AsyncLocalSession() as db:
        await trade_service.buy_trade(db,TradeCreate(trade_id=1,symbol="AAPL",price=100.0,quantity=3))

async def sell_trade_worker():
    async with AsyncLocalSession() as db:
        await trade_service.sell_trade(db,TradeCreate(trade_id=1,symbol="AAPL",price=100.0,quantity=3))


async def test_race_condition():
    tasks=[sell_trade_worker() for _ in range(4)]
    
    results=await asyncio.gather(*tasks,return_exceptions=True)
    success=0
    for result in results:
        if not isinstance(result,Exception):
            success+=1
    
    print(success)
    print(results)