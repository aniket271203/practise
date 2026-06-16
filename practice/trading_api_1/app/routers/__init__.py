from fastapi import APIRouter, HTTPException, Depends
from apis.trading_api_1.app.schemas import TradeCreate, TradeResponse
from typing import List
from apis.trading_api_1.app.services import trade_service
from apis.trading_api_1.app.database import get_db
from sqlalchemy.orm import Session

# depends is used to fetch the database session as it automatically calls get_db and closes the sesion when the function has retuned so you dont have to manually keep track of it everytime 


router=APIRouter(prefix="/trades", tags=["Trades"])


@router.post("/",response_model=TradeResponse, status_code=201)
def create_trade(trade: TradeCreate,db:Session=Depends(get_db)):
    return trade_service.create_trade(db,trade_data=trade)

@router.get('/',response_model=List[TradeResponse])
def get_all_trade(db: Session = Depends(get_db)):
    return trade_service.get_all_trades(db)

@router.get("/{trade_id}",response_model=TradeResponse)
def get_trade_by_id(trade_id: int, db:Session = Depends(get_db)):
    return trade_service.get_trade(db,trade_id)
    
@router.patch("/{trade_id}/cancel",response_model=TradeResponse)
def cancel_trade(trade_id: int, db: Session = Depends(get_db)):
    return trade_service.cancel_trade(db, trade_id)


@router.get('/symbol/{symbol}',response_model=List[TradeResponse])
def get_trade_by_symbol(symbol: str, db: Session = Depends(get_db)):
    return trade_service.get_trade_by_symbol(db, symbol)
