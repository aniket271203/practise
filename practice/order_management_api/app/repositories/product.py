from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from apis.order_management_api.app.models import Product
from typing import List
from apis.order_management_api.app.schemas import ProductCreate
from apis.order_management_api.app.utils import retry
from sqlalchemy.exc import OperationalError

class ProductRepository:
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def create(self,db:AsyncSession,product_data:ProductCreate)->Product:
        product=Product(
            name=product_data.name,
            price=product_data.price,
            stock=product_data.stock
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    
    async def get(self, db:AsyncSession)->List[Product]:
        result=await db.execute(select(Product))
        return result.scalars().all()
    
    @retry(max_attempts=3, delay=1.0, exceptions=(OperationalError,))
    async def get_by_id(self,db:AsyncSession, id:int)->Product:
        result=await db.execute(select(Product).where(Product.id==id))
        return result.scalar_one_or_none()

    async def get_for_update(self,db:AsyncSession, id:int)->Product:
        result=await db.execute(select(Product).where(Product.id==id).with_for_update())
        return result.scalar_one_or_none()
    async def update_stocks(db:AsyncSession,product:Product,quantity:int)->Product:
        product.stock-=quantity
        await db.flush()
        await db.refresh(product)
        return product

product_repository=ProductRepository()