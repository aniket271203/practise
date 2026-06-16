from sqlalchemy import select, func, case,update
from sqlalchemy.orm import selectinload
from app.models import Coupon, Redemption
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, CouponCreate, RedemptionCreate
from typing import List


class CouponRepository:
    async def create(self, db: AsyncSession, coupon_data: CouponCreate) -> Coupon:
        coupon = Coupon(
            code=coupon_data.code,
            max_redemptions=coupon_data.max_redemptions,
            remaining_redemptions=coupon_data.remaining_redemptions,
            discount_percent=coupon_data.discount_percentage
        )
        db.add(coupon)
        await db.commit()
        await db.refresh(coupon)
        return coupon

    async def get_by_id(self, db: AsyncSession, coupon_id: int) -> Coupon:
        result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
        return result.scalar_one_or_none()

    async def get_for_update(self, db: AsyncSession, coupon_id: int) -> Coupon:
        result = await db.execute(select(Coupon).where(Coupon.id == coupon_id).with_for_update())
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, coupon_code: str) -> Coupon:
        result = await db.execute(select(Coupon).where(Coupon.code == coupon_code))
        return result.scalar_one_or_none()

    async def get_top_coupons(self, db: AsyncSession) -> List[Coupon]:
        coupon_redemption_table = (select(Redemption.coupon_id,
                                          func.coalesce(func.count(Redemption.id),0).label("redemption_count"))
                                   .group_by(Redemption.coupon_id).cte('coupon_redemption_table'))

        results = await db.execute(select(Coupon)
                                   .join(
            coupon_redemption_table,
            coupon_redemption_table.c.coupon_id == Coupon.id)
            .order_by(coupon_redemption_table.c.redemption_count.desc())
            .limit(5))

        return results.scalars().all()
    
    async def read_db_chunk(self,db:AsyncSession,last_id,chunk_size=10000):
        result= await db.execute(select(Coupon)
                                 .where(Coupon.id>last_id)
                                 .where(Coupon.processed_at.is_(None))
                                 .order_by(Coupon.id)
                                 .limit(chunk_size))
        
        return result.scalars().all()
    
    async def bulk_updates(self,db:AsyncSession,updates):
        await db.execute(update(Coupon),updates)
        await db.commit()


coupon_repository = CouponRepository()
