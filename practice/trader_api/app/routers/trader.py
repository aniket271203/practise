from fastapi import APIRouter, Depends
from apis.trader_api.app.ratelimiter import check_rate_limit
from apis.trader_api.app.database import get_db
from apis.trader_api.app.auth import verify_api_key
from apis.trader_api.app.schemas import TraderCreate, TraderResponse, PositionResponse, TraderSummary
from sqlalchemy.ext.asyncio import AsyncSession
from apis.trader_api.app.models import Trader
from apis.trader_api.app.services.trader import trader_services
from apis.trader_api.app.services.position import position_services
from typing import List

trader_router = APIRouter(prefix='/traders', tags=["traders"], dependencies=[
                          Depends(verify_api_key), Depends(check_rate_limit)])


@trader_router.post('/', response_model=TraderResponse, status_code=201)
async def create_trader(trader_data: TraderCreate, db: AsyncSession = Depends(get_db)):
    return await trader_services.create_trader(db, trader_data)


@trader_router.get('/', response_model=List[TraderResponse])
async def get_all(db: AsyncSession = Depends(get_db)):
    return await trader_services.get_all(db)


@trader_router.get('/{trader_id}', response_model=TraderResponse)
async def get_by_id(trader_id: int, db: AsyncSession = Depends(get_db)):
    return await trader_services.get_by_id(db, trader_id)


@trader_router.get('/{trader_id}/positions', response_model=List[PositionResponse])
async def get_by_id(trader_id: int, db: AsyncSession = Depends(get_db)):
    return await position_services.get_by_trader_id(db, trader_id)

@trader_router.get('/{id}/summary',response_model=TraderSummary)
async def get_summary(id:int,db:AsyncSession=Depends(get_db)):
    return await trader_services.get_summary(db,id)
