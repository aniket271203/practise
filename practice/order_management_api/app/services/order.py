from sqlalchemy.ext.asyncio import AsyncSession
from apis.order_management_api.app.models import Order
from apis.order_management_api.app.schemas import OrderCreate, OrderStatus
from fastapi import HTTPException
from apis.order_management_api.app.logger import setup_logger
from apis.order_management_api.app.repositories.order import order_repository
from apis.order_management_api.app.repositories.product import product_repository
from typing import List

logger = setup_logger(__name__)


class OrderServices:

    async def create_order(self, db: AsyncSession, order_data: OrderCreate) -> Order:
        logger.info("Creating Order")
        async with db.begin():
            total=0
            products=[]
            for prod in order_data.items:
                product=await product_repository.get_for_update(db,prod.product_id)
                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"product Not Found | id={prod.product_id}"
                    )
                if product.stock<prod.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail="Not enough Products available"
                    )
                total+=product.price*prod.quantity
                await product_repository.update_stocks(db,product,prod.quantity)
                await order_repository.create_items(db,order_data.id,prod,product.price)
                products.append(product)
                
            result = await order_repository.create(db, order_data.user_name,total)
            logger.info(f"Created order | {result.id}")
            return result

    async def get_all(self, db: AsyncSession) -> List[Order]:
        return await order_repository.get(db)

    async def get_by_id(self, db: AsyncSession, id: int) -> Order:
        result = await order_repository.get_by_id(db, id)
        if not result:
            logger.warning(f"order does not exist | id={id}")
            raise HTTPException(
                status_code=404,
                detail=f"order not Found | id={id}"
            )
        return result

    async def update_status(self, db: AsyncSession, id:int, status:OrderStatus)->Order:
        logger.info(f"Updating Status of Order | id={id}")
        order=await self.get_by_id(db,id)
        if status==OrderStatus.CONFIRMED:
            if order.status==OrderStatus.CONFIRMED:
                raise HTTPException(
                    status_code=400,
                    detail="order already Confirmed"
                )
            if order.status==OrderStatus.CANCELLED:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot confirm Cancelled order"
                )
            result=await order_repository.confirm(db,order,status)
            
        if status==OrderStatus.CANCELLED:
            if order.status==OrderStatus.CONFIRMED:
                raise HTTPException(
                    status_code=400,
                    detail="Confirmed Order cannot be Cancelled"
                )
            if order.status==OrderStatus.CANCELLED:
                raise HTTPException(
                    status_code=400,
                    detail="Order already Cancelled"
                )
            async with db.begin():
                items = await order_repository.get_items(
                db,
                order.id)
                for item in items:
                    product = await product_repository.get_for_update(db,item.product_id)

                product.stock += item.quantity
                result=await order_repository.cancel(db,order,status)
                # we need to fetch the orderitems from the orderitem table and for with orderid and then fpr each productid that is in the retuned list we have to update the stocks
            
        logger.info(f"Updated the status sucessflly| id={id}, updated_status={result.status}")
        return result


order_services = OrderServices()
