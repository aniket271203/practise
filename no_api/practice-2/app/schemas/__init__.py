from enum import Enum
from dataclasses import dataclass

class TradeSide(str,Enum):
    BUY="buy"
    SELL="sell"

@dataclass
class TraderCreate:

    name:str
    cash_balance:float

@dataclass
class TradeCreate:
 
    trader_id:int
    symbol:str
    quantity:int
    price:float
    
@dataclass
class PositionCreate:

    trader_id:int
    symbol:str
    quantity:int
    average_price:float

    