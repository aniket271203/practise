from apis.order_management_api.app.schemas import ProductCreate
from sqlalchemy.ext.asyncio import AsyncSession
from apis.order_management_api.app.logger import setup_logger
from apis.order_management_api.app.repositories.product import product_repository
from apis.order_management_api.app.models import Product
from fastapi import HTTPException
from typing import List

logger=setup_logger(__name__)

class ProductServices:
    
    async def create_product(self, db:AsyncSession, product_data:ProductCreate)->Product:
        logger.info("Creating a new product")
        result=await product_repository.create(db,product_data)
        logger.info(f"Product created in DB | id={result.id}")
        return result
        
    async def get_all(self, db:AsyncSession)->List[Product]:
        logger.debug("fetching all products")
        return await product_repository.get(db)
    
    async def get_by_id(self, db:AsyncSession, id:int)->Product:
        logger.warning(f"Fetching Product | id={id}")
        result=await product_repository.get_by_id(db,id)
        if not result:
            logger.warning(f"product does not exist | id={id}")
            raise HTTPException(
                status_code=404,
                detail=f"Product not Found | id={id}"
            )
        return result
    
product_services=ProductServices()