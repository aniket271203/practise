from app.schemas import InventoryCreate, ShipmentStatus
from app.models import Warehouse, Shipment, Product, Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.inventory import inventory_repository
from app.repositories.shipment import shipment_repository


class ShipmentService:
    async def get_shipment(self, db: AsyncSession, shipment_id: int) -> Shipment:
        shipment = await shipment_repository.get_by_id(db, shipment_id=shipment_id)
        if not shipment:
            raise ValueError("status_code=404 detail=Shipment does not exist")

    async def get_shipment_for_update(self, db: AsyncSession, shipment_id: int) -> Shipment:
        shipment = await shipment_repository.get_for_update(db, shipment_id=shipment_id)
        if not shipment:
            raise ValueError("status_code=404 detail=Shipment does not exist")

    async def cancel_shipment(self, db: AsyncSession, shipment_id) -> Shipment:
        async with db.begin():
            shipment = await self.get_shipment_for_update(db, shipment_id)

            if shipment.status == ShipmentStatus.SHIPPED:
                raise ValueError(
                    "status_code=400, detail=Cannot cancel shipped shipment")

            if shipment.status == ShipmentStatus.CANCELLED:
                raise ValueError(
                    "status_code=400, detail=Shipment Already Cancelled")

            inventory = await inventory_repository.get_for_update(db, warehouse_id=shipment.warehouse_id, product_id=shipment.product_id)

            inventory.quantity += shipment.quantity
            shipment.status = ShipmentStatus.CANCELLED

            return shipment
        
    async def mark_shipped(self,db:AsyncSession,shipment_id:int):
        async with db.begin():
            shipment=await self.get_shipment_for_update(db,shipment_id)
            
            if shipment.status==ShipmentStatus.SHIPPED:
                raise ValueError("status_code=400, detail=Shipment already Shipped")
            if shipment.status==ShipmentStatus.CANCELLED:
                raise ValueError("status_code=400, detail=cancelled shipment cannot be shipped")
            shipment.status=ShipmentStatus.SHIPPED
            
    async def get_running_shipment_volume(self,db:AsyncSession):
        shipments=await shipment_repository.get_running_shipment_volume(db)
        return shipments
        
shipment_service=ShipmentService()
