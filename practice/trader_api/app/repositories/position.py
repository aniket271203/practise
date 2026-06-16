from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession
from apis.trader_api.app.models import Position
from apis.trader_api.app.schemas import PositionCreate
from typing import List, Optional

class PositionRepository:
    async def create(self,db:AsyncSession,position_data:PositionCreate)->Position:
        position=Position(
            trader_id=position_data.trader_id,
            symbol=position_data.symbol,
            quantity=position_data.quantity,
            average_price=position_data.average_price
        )
        db.add(position)
        await db.flush()
        await db.refresh(position)
        return position
        
    async def get(self, db:AsyncSession, position_id:int)->List[Position]:
        position=await db.execute(select(Position))
        return position.scalars().all()
    
    async def get_by_trader_id(self,db:AsyncSession,trader_id:int)->List[Position]:
        positions=await db.execute(select(Position).filter(Position.trader_id==trader_id))
        return positions.scalars().all()
    
    async def get_by_id(self,db:AsyncSession,id:int)->Position:
        positions=await db.execute(select(Position).filter(Position.id==id))
        return positions.scalar_one_or_none()
    
    async def get_for_update(self,db:AsyncSession,trader_id:int,symbol:str)->Position:
        positions=await db.execute(select(Position).filter(Position.trader_id==trader_id).filter(Position.symbol==symbol).with_for_update())
        return positions.scalar_one_or_none()
    
    async def get_by_symbol(self,db:AsyncSession,symbol:str)->List[Position]:
        position=await db.execute(select(Position).filter(Position.symbol==symbol.upper()))
        return position.scalars().all()

position_repository=PositionRepository()