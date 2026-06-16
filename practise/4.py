from enum import Enum
from sqlalchemy import Column, func, select, case, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
from fastapi import HTTPException
DATABASE_URL = "sqlite+aiosqlite:///./trading.db"
engine = create_async_engine(DATABASE_URL)

AsyncLocalSession = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncLocalSession() as session:
        try:
            yield session
        finally:
            await session.close()


class Trader(Base):
    __tablename__ = 'traders'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cash_balance = Column(Float, nullable=False)

    trades = relationship('Trade', back_populates='trader')
    positions = relationship("Position", back_populates='trader')


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id'), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    side = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    trader = relationship('Trader', back_populates="trades")


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey('traders.id'), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)

    trader = relationship("Trader", back_populates='positions')


class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeCreate:
    trader_id: int
    symbol: str
    quantity: int
    price: float


async def buy_trade(trade_data: TradeCreate, db: AsyncSession):
    async with db.begin():
        trader_query = select(Trader).where(
            Trader.id == trade_data.trader_id).with_for_update()
        result = await db.execute(trader_query)
        trader = result.scalar_one_or_none()
        if not trader:
            raise HTTPException(
                status_code=404,
                detail="Trader not found"
            )

        if trader.cash_balance < (trade_data.price*trade_data.quantity):
            raise HTTPException(
                status_code=400,
                detail=f"not enough cash_balance | available balance={trader.cash_balance}"
            )
        trader.cash_balance -= (trade_data.price*trade_data.quantity)
        trade = Trade(
            trader_id=trade_data.trader_id,
            symbol=trade_data.symbol,
            quantity=trade_data.quantity,
            price=trade_data.price,
            side=TradeSide.BUY
        )

        db.add(trade)
        await db.flush()

        position_query = select(Position).where(
            Position.trader_id == trade_data.trader_id).where(Position.symbol == trade_data.symbol).with_for_update()
        result = await db.execute(position_query)
        position = result.scalar_one_or_none()
        if not position:
            position = Position(
                trader_id=trader.id,
                symbol=trade_data.symbol,
                quantity=0,
                average_price=0
            )
            db.add(position)
            await db.flush()

        old_qty = position.quantity
        position.quantity = old_qty+trade_data.quantity
        position.average_price = (
            old_qty*position.average_price + trade_data.quantity*trade_data.price)/position.quantity

        return trade


async def sell_trade(trade_data: TradeCreate, db: AsyncSession):
    async with db.begin():
        trader_query = select(Trader).where(
            Trader.id == trade_data.trader_id).with_for_update()
        result = await db.execute(trader_query)
        trader = result.scalar_one_or_none()
        if not trader:
            raise HTTPException(
                status_code=404,
                detail="Trader not found"
            )

        position_query = select(Position).where(
            Position.trader_id == trade_data.trader_id).where(Position.symbol == trade_data.symbol).with_for_update()
        result = await db.execute(position_query)
        position = result.scalar_one_or_none()
        if not position:
            raise HTTPException(
                status_code=400,
                detail="position deos not exist"
            )
        if position.quantity < trade_data.quantity:
            raise HTTPException(
                status_code=400,
                detail="cannot sell more than owned stocks"
            )

        trade = Trade(
            trader_id=trade_data.trader_id,
            symbol=trade_data.symbol,
            quantity=trade_data.quantity,
            price=trade_data.price,
            side=TradeSide.SELL
        )

        db.add(trade)
        await db.flush()

        position.quantity -= trade_data.quantity

        trader.cash_balance += (trade_data.price*trade_data.quantity)

        return trade


async def get_portfolio_summary(trader_id: int, db: AsyncSession):
    result = await db.execute(select(Trader.cash_balance.label('cash_balance')).where(Trader.id == trader_id))
    trader_data = result.first()
    
    result=await db.execute(select(func.count(Position.id).label('position_count')).where(Position.trader_id==trader_id))
    position=result.first()
    
    result = await db.execute(select(func.sum(Position.quantity*Position.average_price).label('portfolio_value')).where(Position.trader_id == trader_id))
    portfolio = result.first()

    return {
        "cash_balance": trader_data.cash_balance,
        "total_positions": position.position_count,
        "portfolio_value": portfolio.portfolio_value
    }


async def get_top_symbols(db:AsyncSession):
    volume=func.sum(Trade.quantity).label('volume')
    
    result=await db.execute(select(Trade.symbol.label('symbol'),volume).group_by(Trade.symbol).order_by(volume.desc()).limit(5))
    
    symbols_data=result.scalars().all()
    return symbols_data

# Task 5

"""
say trade is created and commited and position update fails then what happens 
is that there exists a trade which means a record of a trader buying or 
selling somethign but since the osition was never updated the trader can sell the 
same number of stocks again even if they were suppsoed to be 0 after the 
previuos sell he did 
"""

