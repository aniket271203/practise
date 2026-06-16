from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Warehouse
from app.schemas import WarehouseCreate
from app.repositories.warehouse import warehouse_repository

class WarehouseService:
    async def create_warehouse(self,db:AsyncSession,warehouse_data=WarehouseCreate):
        warehouse=await warehouse_repository.create(db,warehouse_data)
        return warehouse
        
    async def get_top_warehouse(self,db:AsyncSession):
        warehouses=await warehouse_repository.get_top_warehouse(db)
        return warehouses
    
    async def get_warehouse_by_id(self,db:AsyncSession,warehouse_id:int):
        warehouse=await warehouse_repository.get_by_id(db,warehouse_id)
        if not warehouse:
            raise ValueError("status_code=404, detail=Warehouse does not exist")
        return warehouse
    
    async def get_warehouses_above_average_value(self,db:AsyncSession):
        warehouses=await warehouse_repository.get_warehouses_above_average_value(db)
        return warehouses
    
    async def get_warehouse_inventory(self,db:AsyncSession,warehouse_id:int):
        warehouse=await self.get_warehouse_by_id(warehouse_id=warehouse_id)
        
        warehouse_data=await warehouse_repository.get_warehouse_inventory(db,warehouse_id)
        
        return [
            {
                "warehouse_id":warehouse.id,
                "name":warehouse.name,
                "location":warehouse.location,
                "inventories":[
                    {
                        "id":inventory.id,
                        "quantity":inventory.quantity,
                        "product":inventory.product
                    }
                    for inventory in warehouse.inventories
                ]
            }
            for warehouse in warehouse_data
        ]
    
warehouse_service=WarehouseService()