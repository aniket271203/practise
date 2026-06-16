from app.schemas import InventoryCreate, ShipmentCreate, ShipmentStatus
from app.models import Warehouse, Shipment, Product, Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, update, and_, or_
from sqlalchemy.orm import selectinload


class ShipmentRepository:
    async def create(self, db: AsyncSession, inventory_data: InventoryCreate, status: ShipmentStatus) -> Shipment:
        shipment = Shipment(
            warehouse_id=inventory_data.warehouse_id,
            product_id=inventory_data.product_id,
            quantity=inventory_data.quantity,
            status=status
        )
        db.add(shipment)
        await db.flush()
        return shipment

    async def get_by_id(self, db: AsyncSession, shipment_id: int = None, warehouse_id: int = None, product_id: int = None) -> Shipment:
        conditions = []

        if shipment_id:
            conditions.append(Shipment.id == shipment_id)

        if warehouse_id and product_id:
            conditions.append(and_(Shipment.warehouse_id == warehouse_id,
                                   Shipment.product_id == product_id))

        if not conditions:
            return None

        result = await db.execute(
            select(
                Shipment
            )
            .where(
                or_(*conditions)
            )
        )
        return result.scalar_one_or_none()

    async def get_for_update(self, db: AsyncSession, shipment_id: int = None, warehouse_id: int = None, product_id: int = None) -> Shipment:
        conditions = []

        if shipment_id:
            conditions.append(Shipment.id == shipment_id)

        if warehouse_id and product_id:
            conditions.append(and_(Shipment.warehouse_id == warehouse_id,
                                   Shipment.product_id == product_id))

        if not conditions:
            return None

        result = await db.execute(
            select(
                Shipment
            )
            .where(
                or_(*conditions)
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()
    
    async def get_running_shipment_volume(self,db:AsyncSession):
        result= await db.execute(
            select(
                Shipment.id,
                Shipment.quantity,
                func.sum(Shipment.quantity).over(partition_by=Shipment.product_id,order_by=Shipment.created_at).label('running_total')
            )
        )
        
        return result.mappings().all()


shipment_repository = ShipmentRepository()
