from app.schemas import WarehouseCreate
from app.models import Warehouse, Shipment, Product, Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, update, and_, or_
from sqlalchemy.orm import selectinload
from typing import List


class WarehouseRepository:
    async def create(self, db: AsyncSession, warehouse_data: WarehouseCreate) -> Warehouse:
        warehouse = Warehouse(
            name=warehouse_data.name,
            location=warehouse_data.location
        )
        db.add(warehouse)
        await db.commit()
        return warehouse

    async def get_all(self, db: AsyncSession) -> List[Warehouse]:
        result = await db.execute(select(Warehouse))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, warehouse_id: int) -> Warehouse:
        result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
        return result.scalar_one_or_none()

    async def get_for_update(self, db: AsyncSession, warehouse_id: int) -> Warehouse:
        result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id).with_for_update())
        return result.scalar_one_or_none()

    async def get_top_warehouse(self, db: AsyncSession):
        inventory_value_table = (select(Inventory.warehouse_id,
                                        func.sum(Inventory.quantity*Product.price).label('inventory_value'))
                                 .select_from(Inventory)
                                 .join(Product, Product.id == Inventory.product_id)
                                 .group_by(Inventory.warehouse_id)
                                 .cte('inventory_value_table')
                                 )

        result = await db.execute(
            select(
                inventory_value_table.c.warehouse_id,
                inventory_value_table.c.inventory_value
            )
            .order_by(
                inventory_value_table.c.inventory_value.desc()
            )
            .limit(5)
        )

        return result.mappings().all()
    
    async def get_warehouses_above_average_value(self, db: AsyncSession):
        inventory_value_table = (select(Inventory.warehouse_id,
                                        func.sum(Inventory.quantity*Product.price).label('inventory_value'))
                                 .select_from(Inventory)
                                 .join(Product, Product.id == Inventory.product_id)
                                 .group_by(Inventory.warehouse_id)
                                 .cte('ininventory_value_tableventory')
                                 )
        
        average_inventory_value=(select(func.avg(inventory_value_table.c.inventory_value)).scalar_subquery())

        result = await db.execute(
            select(
                inventory_value_table.c.warehouse_id,
                Warehouse.name,
                inventory_value_table.c.inventory_value
            )
            .select_from(inventory_value_table)
            .join(Warehouse,Warehouse.id==inventory_value_table.c.warehouse_id)
            .where(
                inventory_value_table.c.inventory_value>average_inventory_value
            )
        )

        return result.mappings().all()
    
    async def get_warehouse_inventory(self,db:AsyncSession,warehouse_id:int)->Warehouse:
        result=await db.execute(select(Warehouse).options(selectinload(Warehouse.inventorys).selectinload(Inventory.product)).where(Warehouse.id==warehouse_id))
        return result.scalar_one_or_none()

warehouse_repository = WarehouseRepository()
