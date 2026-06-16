from app.database import engine,Base,AsyncLocalSession
import asyncio
from app.schemas import ProductCreate, ShipmentCreate,InventoryCreate,WarehouseCreate
from app.services.product import product_service
from app.services.warehouse import warehouse_service

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def main():
    await create_tables()
    
    async with AsyncLocalSession() as db:
        # await product_service.create_product(db,ProductCreate(name="laptop",price=100.0))
        products= await product_service.get_product_by_id(db,product_id=5)
        print(products)
        # warehouse=await warehouse_service.create_warehouse(db,WarehouseCreate(name="WR-4",location="India"))
        # warehouse=await warehouse_service.get_warehouse_by_id(db,warehouse_id=3)
        # print(warehouse)
        
if __name__=="__main__":
    asyncio.run(main())
    