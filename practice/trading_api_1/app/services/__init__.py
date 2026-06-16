from apis.trading_api_1.app.schemas import TradeCreate, TradeStatus
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List,Optional
from apis.trading_api_1.app.models import Trade
from apis.trading_api_1.app.repositories import trade_repository
from apis.trading_api_1.app.logger import setup_logger

logger=setup_logger(__name__)

class TradeServices:
    def create_trade(self,db:Session,trade_data:TradeCreate)->Trade:
        logger.info(f"Creating Trade | id={trade_data.id}")
        trade=trade_repository.create_trade(db,trade_data)
        logger.info(f"Created Trade successfully | id={trade.id}")
        return trade
    
    def get_trade(self,db:Session,trade_id:int)->Optional[Trade]:
        logger.debug(f"fetching trade| id={trade_id}")  
        trade=trade_repository.get_trade(db,trade_id)
        if not trade:
            logger.warning(f"Trade not found| id= {trade_id}")
            raise HTTPException(status_code=404, detail="trade not found")      
        return trade
    
    def get_all_trades(self,db:Session)->List[Trade]:
        logger.debug("Fetching all trades")
        trades=trade_repository.get_all_trades(db)
        return trades
    
    def get_trade_by_symbol(self,db:Session,symbol:str)->Optional[Trade]:
        logger.debug(f"fetching trades| symbol={symbol}")  
        trades=trade_repository.get_trade_by_symbol(db,symbol)
        if not trades:
            logger.warning(f"Trades not found| symbol= {symbol}")
            raise HTTPException(status_code=404, detail=f"trades not found for {symbol}")      
        return trades
    
    def cancel_trade(self,db:Session,trade_id:int)->Trade:
        logger.info(f"Cancelling Trade| id={trade_id}")
        trade=self.get_trade(db,trade_id)
        if trade.status==TradeStatus.CANCELLED:
            logger.warning(f"Cancelled Trade cannot be cancelled")
            raise HTTPException(status_code=400, detail="trade already cancelled")
        if trade.status==TradeStatus.FILLED:
            logger.warning(f"Filled trade cannot be cancelled")
            raise HTTPException(status_code=400, detail="cannot cancel filled trade")
        trade=trade_repository.update_status(db,trade,TradeStatus.CANCELLED)
        logger.info(f"Cancelled Trade | id={trade_id}")
        return trade
    
trade_services=TradeServices()
        