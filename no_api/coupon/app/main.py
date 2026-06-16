from app.database import Base,engine,AsycnLocalSession
import asyncio

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def main():
    await create_tables()
    
    async with AsycnLocalSession() as db:
        pass
    
if __name__=="__main__":
    asyncio.run(main())
    