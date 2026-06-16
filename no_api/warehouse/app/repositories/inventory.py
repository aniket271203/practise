from app.schemas import InventoryCreate
from app.models import Warehouse, Shipment, Product, Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, update, and_, or_
from sqlalchemy.orm import selectinload


class InventoryRepository:
    async def create(self, db: AsyncSession, inventory_data: InventoryCreate) -> Inventory:
        inventory = Inventory(
            warehouse_id=inventory_data.warehouse_id,
            product_id=inventory_data.product_id,
            quantity=inventory_data.quantity
        )
        db.add(inventory)
        await db.flush()
        return inventory

    async def get_by_id(self, db: AsyncSession, inventory_id: int = None, warehouse_id: int = None, product_id: int = None) -> Inventory:
        conditions = []

        if inventory_id:
            conditions.append(Inventory.id == inventory_id)

        if warehouse_id and product_id:
            conditions.append(
                and_(
                    Inventory.warehouse_id == warehouse_id,
                    Inventory.product_id == product_id
                )
            )

        result = await db.execute(
            select(
                Inventory
            )
            .where(
                or_(*conditions)
            )
        )
        return result.scalar_one_or_none()

    async def get_for_update(self, db: AsyncSession, inventory_id: int = None, warehouse_id: int = None, product_id: int = None) -> Inventory:
        conditions = []

        if inventory_id:
            conditions.append(Inventory.id == inventory_id)

        if warehouse_id and product_id:
            conditions.append(
                and_(
                    Inventory.warehouse_id == warehouse_id,
                    Inventory.product_id == product_id
                )
            )

        result = await db.execute(
            select(
                Inventory
            )
            .where(
                or_(*conditions)
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async  def get_summary(self,db:AsyncSession):
        result= await db.execute(
            select(
                func.count(func.distinct(Inventory.product_id)).label('total_products'),
                func.sum(Inventory.quantity).label('total_stock')                
            )
        )
        
        return result.mappings().all()
    
    async def read_db_chunk(self,db:AsyncSession,last_id:int,chunk_size:int):
        result= await db.execute(select(Inventory)
                                 .where(and_(Inventory.id>last_id,Inventory.processed_at.is_(None)))
                                 .order_by(Inventory.id)
                                 .limit(chunk_size))
        
        return result.scalars().all()
    
    async def bulk_updates(self,db:AsyncSession,updates):
        await db.execute(update(Inventory),updates)
        await db.commit()
    
inventory_repository = InventoryRepository()
