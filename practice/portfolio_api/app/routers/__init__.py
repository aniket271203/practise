from fastapi import APIRouter, Depends
from apis.portfolio_api.app.ratelimiter import check_rate_limit
from apis.portfolio_api.app.schemas import PositionResponse, PositionCreate
from apis.portfolio_api.app.services import portfolio_services
from sqlalchemy.ext.asyncio import AsyncSession
from apis.portfolio_api.app.database import get_db
from typing import List, Optional
from apis.portfolio_api.app.auth import verify_api_key
router=APIRouter(prefix="/portfolio", tags=["portfolio"], dependencies=[Depends(check_rate_limit),Depends(verify_api_key)])


@router.post('/positions', response_model=PositionResponse, status_code=201)
async def create_postions(position_data:PositionCreate, db:AsyncSession = Depends(get_db)):
    return await portfolio_services.create_position(db,position_data)

@router.get("/position",response_model=List[PositionResponse])
async def get_position(db:AsyncSession=Depends(get_db)):
    return await portfolio_services.get_all_positions(db)

@router.get('/positions/{id}', response_model=PositionResponse)
async def get_position_by_id(id:int,db:AsyncSession=Depends(get_db)):
    return await portfolio_services.get_position_by_id(db,id)

@router.patch('/positions/{id}/update', response_model=PositionResponse)
async def update_position(id:int,quantity:int,avg_price:float,db:AsyncSession=Depends(get_db)):
    return await portfolio_services.update_position(db,id,quantity,avg_price)

@router.delete('/positions/{id}',response_model=PositionResponse)
async def delete_position(id:int, db:AsyncSession= Depends(get_db)):
    return await portfolio_services.delete_position(db,id)

@router.get('/positions/value/total')
async def get_total_value(db:AsyncSession=Depends(get_db)):
    return await portfolio_services.get_total_portfolio_value(db)
