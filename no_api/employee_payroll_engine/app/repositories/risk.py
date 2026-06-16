from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Department,Employee,Payroll
from sqlalchemy import select,case, func,update,text

class RiskRepository:
    async def set_up(self,db:AsyncSession):
        await db.execute(text("""ALTER TABLE payrolls ADD COLUMN IF NOT EXISTS risk_score REAL"""))
        await db.execute(text("""ALTER TABLE payrolls ADD COLUMN IF NOT EXISTS processed_at DATETIME"""))
        await db.commit()
    
    async def get_chunks(self,db:AsyncSession,last_id:int,chunk_size:int):
        results= await db.execute(select(Payroll)
                                  .where(Payroll.id>last_id)
                                  .where(Payroll.processed_at.is_(None))
                                  .order_by(Payroll.id)
                                  .limit(chunk_size))
        
        return results.scalars().all()
    
    async def bulk_updates(self,db:AsyncSession,updates):
        
        await db.execute(update(Payroll),updates)
        await db.commit()

risk_repository=RiskRepository()