from sqlalchemy.orm import Session
from apis.trading_api_1.app.models import Trade
from apis.trading_api_1.app.schemas import TradeCreate, TradeStatus
from typing import Optional, List

class TradeRepository:
    def create_trade(self,db: Session,trade_data:TradeCreate)->Trade:
        new_trade=Trade(
            id=trade_data.id,
            quantity=trade_data.quantity,
            price=trade_data.price,
            status=TradeStatus.PENDING
        )
        db.add(new_trade)
        db.commit()
        db.refresh(new_trade)
        return new_trade
    
    def get_trade(self,db:Session,trade_id: int)->Optional[Trade]:
        return db.query(Trade).filter(Trade.id==trade_id).first()
    
    def get_all_trades(self,db:Session)->List[Trade]:
        return db.query(Trade).all()
    
    def get_trade_by_symbol(self,db:Session, symbol: str)->Optional[Trade]:
        return db.query(Trade).filter(Trade.symbol==symbol).all()
    
    def update_status(self,db:Session,trade:Trade,status:TradeStatus)->Trade:
        trade.status=status
        db.commit()
        db.refresh(trade)
        return trade
    
    
trade_repository=TradeRepository()