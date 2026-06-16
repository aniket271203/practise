from app.schemas import InventoryCreate, ShipmentStatus
from app.models import Warehouse, Shipment, Product, Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.inventory import inventory_repository
from app.repositories.shipment import shipment_repository
from app.services.warehouse import warehouse_service
from app.services.product import product_service
from random import random
from datetime import datetime,timezone
from app.utils.multiprocessing import run_parallel,chunk_lists

class InventoryService:
    async def add_inventory(self,db:AsyncSession,inventory_data:InventoryCreate):
        async with db.begin():
            # check warehouse exists
            warehouse=await warehouse_service.get_warehouse_by_id(db,inventory_data.warehouse_id)
            
            # check product exists
            product= await product_service.get_product_by_id(db,inventory_data.product_id)
            
            # check if inventory exists
            inventory=await inventory_repository.get_for_update(db,warehouse_id=inventory_data.warehouse_id,product_id=inventory_data.product_id)
            if not inventory:
                # if not then create one 
                inventory=await inventory_repository.create(db,inventory_data)
                return inventory
            
            # if it exists update the quantity
            inventory_data.quantity+=inventory_data.quantity

            return inventory
        
    async def reserve_inventory(self,db:AsyncSession,inventory_data:InventoryCreate):
        async with db.begin():
            
            # check warehouse exists
            warehouse=await warehouse_service.get_warehouse_by_id(db,inventory_data.warehouse_id)
            
            # check product exists
            product= await product_service.get_product_by_id(db,inventory_data.product_id)
            
            # check if inventory exists
            inventory=await inventory_repository.get_for_update(db,warehouse_id=inventory_data.warehouse_id,product_id=inventory_data.product_id)
            if not inventory:
                # if not raise error
                raise ValueError("status_code=404, detail=Inventory does not exist")
            
            if inventory.quantity<inventory_data.quantity:
                # if yes validate that the quantoty is available
                raise ValueError("status_code=400, detail=Cannot reserve more than available quantity")
            
            # create shipment
            try:
                await shipment_repository.create(db,inventory_data,ShipmentStatus.RESERVED)
            except Exception as e:
                raise e
            
            # update the quantity
            inventory_data.quantity-=inventory_data.quantity

            return inventory
        
    async def get_inventory_summary(self,db:AsyncSession):
        inventory_stats=await inventory_repository.get_summary(db)
        return inventory_stats
    
    def random_factor(self):
        return random(0,1)
    
    def process_chunk(self,rows):
        results=[]
        
        for row in rows:
            risk_score= row.quantity*row.price*self.random_factor()
            processed_at=datetime.now(timezone.utc)
            results.append({'id':int(row.id),'risk_score':risk_score,'processed_at':processed_at})
        
        return results
    
    async def process_risk_score(self,db:AsyncSession):
        
        last_id=0
        chunk_size=10000
        while True:
            db_chunk=await inventory_repository.read_db_chunk(db,last_id,chunk_size)
            
            if not db_chunk:
                break
            
            chunks=chunk_lists(db_chunk)
            results=run_parallel(self.process_chunk,chunks)
            
            flattened=[]
            for res in results:
                flattened.extend(res)
            
            await inventory_repository.bulk_updates(db,flattened)
            last_id=db_chunk[-1].id  
            
inventory_service=InventoryService()