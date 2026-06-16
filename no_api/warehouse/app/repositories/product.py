from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Product, Inventory
from app.schemas import ProductCreate
from typing import List
from sqlalchemy import select, func, update


class ProductRepository:
    async def create(self, db: AsyncSession, product_data: ProductCreate) -> Product:
        product = Product(
            name=product_data.name,
            price=product_data.price
        )
        db.add(product)
        await db.commit()
        return product

    async def get_all(self, db: AsyncSession) -> List[Product]:
        result = await db.execute(select(Product))

        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, product_id: int) -> Product:
        result = await db.execute(select(Product).where(Product.id == product_id))

        return result.scalar_one_or_none()

    async def get_products_above_average_stock(self, db: AsyncSession):

        product_stocks_table = (select
                                (
                                    Product.id,
                                    Product.name,
                                    func.sum(Inventory.quantity).label(
                                        'product_stocks')
                                )
                                .select_from(Product)
                                .join(Inventory, Inventory.product_id == Product.id)
                                .group_by(Product.id, Product.name)
                                .cte('product_stocks_table')
                                )
        average_product_stocks = (
            select(func.avg(product_stocks_table.c.product_stocks)).scalar_subquery())

        result = await db.execute(
            select(
                product_stocks_table.c.id,
                product_stocks_table.c.name,
                product_stocks_table.c.product_stocks
            )
            .where(product_stocks_table.c.product_stocks>average_product_stocks)
        )

        return result.mappings().all()


product_repository = ProductRepository()
