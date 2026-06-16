from fastapi import FastAPI
from app.database import Base,engine


    
app=FastAPI(title="Trade API",description="Tradeing practise",version="1.0.0")

@app.on_event("startup")
async def start_up():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def health_check():
    return {"status":"ok","message":"everythign works perfectly"}