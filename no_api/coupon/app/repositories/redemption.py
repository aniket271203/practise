from sqlalchemy import select, func, case, or_, and_
from sqlalchemy.orm import selectinload
from app.models import Redemption
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, CouponCreate, RedemptionCreate


class RedemptionRepository:
    async def create(self, db: AsyncSession, redemption_data: RedemptionCreate) -> Redemption:
        redemption = Redemption(
            user_id=redemption_data.user_id,
            coupon_id=redemption_data.coupon_id
        )
        db.add(redemption)
        await db.flush()
        return redemption

    async def get_by_id(self, db: AsyncSession, redemption_id: int = None, user_id: int = None, coupon_id: int = None) -> Redemption:
        conditions=[]
        if redemption_id:
            conditions.append((Redemption.id==redemption_id))
        
        if user_id and coupon_id:
            conditions.append(and_(
                Redemption.coupon_id==coupon_id,
                Redemption.user_id==user_id
            ))
                
        result = await db.execute(select(Redemption).where(or_(*conditions)))
        return result.scalar_one_or_none()


redemption_repository = RedemptionRepository()
