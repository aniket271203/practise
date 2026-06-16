from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Trade, Trader
from app.schemas import TradeCreate, TraderCreate, PositionCreate, TradeSide
from app.repositories.trader import trader_repository
from app.repositories.trade import trade_repository
from app.repositories.position import position_repository


class TradeService:
    async def get_trades(self,db:AsyncSession):
        trades=await trade_repository.get_all(db)
        return trades
    
    async def buy_trade(self, db: AsyncSession, trade_data: TradeCreate):
        async with db.begin():
            # validate the user exists
            trader = await trader_repository.get_for_update(db, trade_data.trader_id)

            if not trader:
                # should be a HTTPException
                raise ValueError(" status_code=404, detail=trader not Found")

            # Validate he has enough cash
            if trader.cash_balance < trade_data.price*trade_data.quantity:
                raise ValueError(
                    " status_code=400, detail=Trader does not have enough Cash")

            # Create Trade
            try:
                trade = await trade_repository.create(db, trade_data, TradeSide.BUY)
            except Exception as e:
                raise e

            # update Position
            position = await position_repository.get_for_update(db, trade_data.trader_id, trade_data.symbol)

            if not position:
                try:
                    position = await position_repository.create(db, PositionCreate(trader_id=trade_data.trader_id, symbol=trade_data.symbol, quantity=0, average_price=0))
                except Exception as e:
                    raise e

                position = await position_repository.get_for_update(db, trade_data.trader_id, trade_data.symbol)

            # Update weighted average price
            old_qty = position.quantity
            position.quantity += trade_data.quantity
            position.average_price = (old_qty*position.average_price + trade_data.quantity *
                                      trade_data.price)/(position.quantity+old_qty)

            # deduct cash
            trader.cash_balance -= (trade_data.price*trade_data.quantity)

            return trade

    async def sell_trade(self, db: AsyncSession, trade_data: TradeCreate):
        async with db.begin():
            # Trader must exist as the locking order should be same
            trader = await trader_repository.get_for_update(db, trade_data.trader_id)

            if not trader:
                # should be a HTTPException
                raise ValueError(" status_code=404, detail=trader not Found")

            # position must exist
            position = await position_repository.get_for_update(db, trade_data.trader_id, trade_data.symbol)

            if not position:
                # should be a HTTPException
                raise ValueError(" status_code=404, detail=position not Found")

            if position.quantity < trade_data.quantity:
                raise ValueError(
                    "status_code=400, detail=Connot sell more than owned")

            # Create Trade
            try:
                trade = await trade_repository.create(db, trade_data, TradeSide.SELL)
            except Exception as e:
                raise e

            # update position
            position.quantity -= trade_data.quantity

            if position.quantity == 0:
                await position_repository.delete(db, position)

            # add Cash
            trader.cash_balance += (trade_data.price*trade_data.quantity)

            return trade

    async def get_symbols_above_average_volume(self, db: AsyncSession):
        symbols = await trade_repository.get_symbols_above_average_volume(db)
        return symbols

    async def get_running_trade_value(self, db: AsyncSession):
        trades = await trade_repository.get_running_trade_value(db)
        return trades


trade_service = TradeService()
