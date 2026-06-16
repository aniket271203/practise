from fastapi import APIRouter, Depends
from apis.order_management_api.app.database import get_db
from apis.order_management_api.app.ratelimiter import check_rate_limit
from apis.order_management_api.app.auth import verify_api_key
from apis.order_management_api.app.schemas import ProductCreate, ProductResponse
from apis.order_management_api.app.services.product import product_services
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

product_router = APIRouter(prefix="/products", tags=["products"], dependencies=[
                           Depends(check_rate_limit), Depends(verify_api_key)])


@product_router.post('/', response_model=ProductResponse, status_code=201)
async def create_product(product_data: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await product_services.create_product(db, product_data)


@product_router.get('/', response_model=List[ProductResponse])
async def get_products(db: AsyncSession = Depends(get_db)):
    return await product_services.get_all(db)


@product_router.get('/{id}', response_model=ProductResponse)
async def get_product_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await product_services.get_by_id(db,id)