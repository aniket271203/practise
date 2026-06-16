from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Warehouse
from app.schemas import ProductCreate
from app.repositories.product import product_repository

class ProductService:
    async def create_product(self,db:AsyncSession,product_data:ProductCreate):
        product=await product_repository.create(db,product_data)
        return product
    
    async def get_product_by_id(self,db:AsyncSession,product_id:int):
        product=await product_repository.get_by_id(db,product_id)
        if not product:
            raise ValueError("status_code=404, detail=Product does not exist")
        return product
    
    async def get_products_above_average_stock(self,db:AsyncSession):
        products=await product_repository.get_products_above_average_stock(db)
        return products
    
product_service=ProductService()