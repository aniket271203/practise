from fastapi import APIRouter, Depends
from apis.trader_api.app.database import get_db
from apis.trader_api.app.services.position import position_services
from apis.trader_api.app.ratelimiter import check_rate_limit
from apis.trader_api.app.auth import verify_api_key
from apis.trader_api.app.schemas import PositionCreate, PositionResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

position_router = APIRouter(prefix="/positions", tags=["positions"], dependencies=[
                            Depends(check_rate_limit), Depends(verify_api_key)])


@position_router.get('/{id}', response_model=PositionResponse)
async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await position_services.get_by_id(db, id)


@position_router.get('/', response_model=List[PositionResponse])
async def get_by_symbol(symbol: str, db: AsyncSession = Depends(get_db)):
    return await position_services.get_by_symbol(db, symbol)
