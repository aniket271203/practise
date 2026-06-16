from fastapi import APIRouter, Depends
from apis.trading_practise_api.app.schemas import TradeCreate,TradeResponse,TraderResponse,TradeStatus
from typing import List
from apis.trading_practise_api.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from apis.trading_practise_api.app.services.trades import trade_services
from apis.trading_practise_api.app.ratelimiter import check_rate_limit

router=APIRouter(prefix="/trades",tags=["trades"], dependencies=[Depends(check_rate_limit)])

database={}
counter=0

@router.post("/", response_model=TradeResponse,status_code=201)
async def create_trade(trade_data:TradeCreate, db:AsyncSession=Depends(get_db)):
    return await trade_services.create_trade(db,trade_data)

@router.get('/',response_model=List[TradeResponse])
async def get_all(db:AsyncSession=Depends(get_db)):
    return await trade_services.get_all(db)

@router.get('/{trades_id}',response_model=TradeResponse)
async def get_trade_by_id(trade_id:int,db:AsyncSession=Depends(get_db)):
    return await trade_services.get_trade_by_id(db,trade_id)

@router.patch('/{trade_id}/fill',response_model=TradeResponse)
async def update_status(trade_id:int,db:AsyncSession=Depends(get_db)):
    return await trade_services.update_status(db,trade_id,TradeStatus.FILLED)

@router.patch('/{trade_id}/cancel',response_model=TradeResponse)
async def cancel_trade(trade_id:int,db:AsyncSession=Depends(get_db)):
    return await trade_services.update_status(db,trade_id,TradeStatus.CANCELLED)

@router.get('/trader/{trader_id}',response_model=List[TradeResponse])
async def get_trader(trader_id:int,db:AsyncSession=Depends(get_db)):
    return await trade_services.get_trader(db,trader_id)