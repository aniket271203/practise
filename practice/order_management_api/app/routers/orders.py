from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from apis.order_management_api.app.database import get_db
from apis.order_management_api.app.schemas import OrderCreate, OrderResponse,OrderStatus
from apis.order_management_api.app.ratelimiter import check_rate_limit
from apis.order_management_api.app.auth import verify_api_key
from typing import List
from apis.order_management_api.app.services.order import order_services

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(check_rate_limit), Depends(verify_api_key)])


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await order_services.create_order(db, order_data)

@router.get("/{id}", response_model=OrderResponse)
async def get_order_by_id(id:int, db:AsyncSession=Depends(get_db)):
    return await order_services.get_by_id(db,id)

@router.get('/', response_model=List[OrderResponse])
async def get_orders(db:AsyncSession=Depends(get_db)):
    return await order_services.get_all(db)

@router.patch('/{id}/confirm', response_model=OrderResponse)
async def confirm_order(id:int, db:AsyncSession=Depends(get_db)):
    return await order_services.update_status(db,id,OrderStatus.CONFIRMED)

@router.patch('/{id}/cancel', response_model=OrderResponse)
async def cancel_order(id:int, db:AsyncSession=Depends(get_db)):
    return await order_services.update_status(db,id,OrderStatus.CANCELLED)
