from fastapi import APIRouter, HTTPException, Depends
from apis.trading_api.app.schemas import TradeCreate, TradeResponse
from typing import List
from apis.trading_api.app.services import trade_service
from apis.trading_api.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from apis.trading_api.app.ratelimiter import check_rate_limit
from apis.trading_api.app.auth import verify_api_key
# depends is used to fetch the database session as it automatically calls get_db and closes the sesion when the function has retuned so you dont have to manually keep track of it everytime


router = APIRouter(
    prefix="/trades", tags=["Trades"], dependencies=[Depends(check_rate_limit),Depends(verify_api_key) ])


@router.post("/", response_model=TradeResponse, status_code=201)
async def create_trade(trade: TradeCreate, db: AsyncSession = Depends(get_db)):
    return await trade_service.create_trade(db, trade_data=trade)


@router.get('/', response_model=List[TradeResponse])
async def get_all_trade(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    if limit > 100:
        limit = 100  # had cap on number of enteries returned
    return await trade_service.get_all_trades(db, skip=skip, limit=limit)


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade_by_id(trade_id: int, db: AsyncSession = Depends(get_db)):
    return await trade_service.get_trade(db, trade_id)


@router.patch("/{trade_id}/cancel", response_model=TradeResponse)
async def cancel_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    return await trade_service.cancel_trade(db, trade_id)


@router.get('/symbol/{symbol}', response_model=List[TradeResponse])
async def get_trade_by_symbol(symbol: str, db: AsyncSession = Depends(get_db)):
    return await trade_service.get_trade_by_symbol(db, symbol)
