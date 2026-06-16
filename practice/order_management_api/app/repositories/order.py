from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from apis.order_management_api.app.models import Order,Product,OrderItem
from typing import List
from apis.order_management_api.app.schemas import OrderCreate,OrderStatus,OrderItemCreate
from apis.order_management_api.app.utils import retry
from sqlalchemy.exc import OperationalError

class OrderRepository:
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def create(self,db:AsyncSession,name:str, total:float)->Order:
        order=Order(
            user_name=name,
            total_amount=total,
            status=OrderStatus.PENDING
        )
        db.add(order)
        await db.flush()
        await db.refresh(order)
        return order
    
    async def create_items(self,db:AsyncSession,id:int,item:OrderItem,price:float)->OrderItem:
        order_item=OrderItem(
            order_id=id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=price
        )
        db.add(order_item)
        await db.flush()
        await db.refresh(order_item)
        return order_item
    
    async def get(self, db:AsyncSession)->List[Order]:
        result=await db.execute(select(Order))
        return result.scalars().all()
    
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def get_by_id(self,db:AsyncSession, id:int)->Order:
        result=await db.execute(select(Order).where(Order.id==id))
        return result.scalar_one_or_none()
    
    async def confirm(self,db:AsyncSession,order:Order,status:OrderStatus):
        order.status=status
        await db.commit()
        await db.refresh(order)
        return order
    
    async def cancel(self,db:AsyncSession,order:Order,status:OrderStatus):
        order.status=status
        await db.flush()
        await db.refresh(order)
        return order
    
    async def get_items(self,db: AsyncSession,order_id: int):
        result = await db.execute(
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
        )

        return result.scalars().all()
    
order_repository=OrderRepository()