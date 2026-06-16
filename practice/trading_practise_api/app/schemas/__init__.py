from pydantic import BaseModel, validator
from enum import Enum
from email_validator import validate_email


class TradeStatus(str, Enum):
    FILLED = "filled"
    CANCELLED = "cancelled"
    PENDING = "pending"


class TradeExchange(str, Enum):
    NSE = "nse"
    BSE = "bse"
    NYSE = "nyse"
    NASDAQ = "nasdaq"
    BINANCE = "binance"


class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeCreate(BaseModel):
    symbol: str
    quantity: int
    price: float
    exchange: TradeExchange
    side: str
    trader_id:int

    @validator('symbol')
    def check_symbol(cls, v):
        if not v.isalpha():
            raise ValueError('symbol must contain only letters')
        return v.upper()

    @validator('quantity')
    def quantity_mus_be_positive(cls, v):
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("price must be positive")
        return v


class TraderDesk(str, Enum):
    EQUITY = "equity"
    DERIVATIVES = "derivatives"
    CRYPTO = "crypto"


class TraderCreate(BaseModel):
    name: str
    email: str
    desk: TraderDesk

    @validator('name')
    def name_is_nonempty(cls, v):
        if not v:
            raise ValueError("name cannot be empty")
        return v

    @validator('email')
    def check_email(cls, v):
        if not validate_email(v):
            raise ValueError(" email must contain @ and .")
        return v


class TradeResponse(BaseModel):
    id: int
    symbol: str
    quantity: int
    price: float
    side: TradeSide
    status: TradeStatus
    exchange: TradeExchange
    # trader_id: int

    class Config:
        from_attribute = True


class TraderResponse(BaseModel):
    id: int
    name: str
    email: str
    desk: TraderDesk
    is_active: bool

    class Config:
        from_attributes = True
