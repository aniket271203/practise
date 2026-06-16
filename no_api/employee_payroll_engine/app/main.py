from app.database import engine,Base,AsyncLocalSession
import asyncio
from app.services.employee import employee_services

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def main():
    await create_tables()
    
    async with AsyncLocalSession() as session:
        await employee_services.create_employee(session)

if __name__=="__main__":
    asyncio.run(main())