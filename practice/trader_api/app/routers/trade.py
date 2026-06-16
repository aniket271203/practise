from fastapi import APIRouter, Depends
from apis.trader_api.app.database import get_db
from apis.trader_api.app.services.trade import trade_services
from apis.trader_api.app.ratelimiter import check_rate_limit
from apis.trader_api.app.auth import verify_api_key
from apis.trader_api.app.schemas import TradeResponse, TradeCreate, TradeSide
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

trade_router = APIRouter(prefix="/trades", tags=["trades"], dependencies=[
                         Depends(check_rate_limit), Depends(verify_api_key)])


@trade_router.post('/buy', response_model=TradeResponse, status_code=201)
async def buy_trade(trade_data: TradeCreate, db: AsyncSession = Depends(get_db)):
    return await trade_services.buy_trade(db, trade_data)


@trade_router.post('/sell', response_model=TradeResponse, status_code=201)
async def sell_trade(trade_data: TradeCreate, db: AsyncSession = Depends(get_db)):
    return await trade_services.sell_trade(db, trade_data)


@trade_router.get('/{id}', response_model=TradeResponse)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await trade_services.get_by_id(db, id)


@trade_router.get('/', response_model=List[TradeResponse])
async def get_all(symbol: str = None, trader_id: int = None, side: TradeSide = None, db: AsyncSession = Depends(get_db)):
    return await trade_services.get_all(db, symbol, trader_id, side)
