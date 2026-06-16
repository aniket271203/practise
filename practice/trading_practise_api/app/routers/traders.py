from fastapi import Request, APIRouter, Depends
from apis.trading_practise_api.app.database import get_db
from apis.trading_practise_api.app.schemas import TraderResponse, TraderCreate
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from apis.trading_practise_api.app.services.traders import trader_services
from apis.trading_practise_api.app.ratelimiter import check_rate_limit

trader_router = APIRouter(prefix="/trader", tags=["traders"], dependencies=[Depends(check_rate_limit)])


@trader_router.post('/', response_model=TraderResponse, status_code=201)
async def create_trader(trader_data: TraderCreate, db: AsyncSession = Depends(get_db)):
    return await trader_services.create_trader(db, trader_data)

@trader_router.get('/', response_model=List[TraderResponse])
async def get_all(db: AsyncSession = Depends(get_db)):
    return await trader_services.get_all(db)

@trader_router.get('/{trader_id}', response_model=TraderResponse)
async def get_trader_by_id(trader_id: int, db: AsyncSession = Depends(get_db)):
    return await trader_services.get_trader_by_id(db, trader_id)

@trader_router.delete('/{trader_id}', response_model=TraderResponse)
async def delete_trader(trader_id: int, db: AsyncSession = Depends(get_db)):
    return await trader_services.delete_trader(db,trader_id)
