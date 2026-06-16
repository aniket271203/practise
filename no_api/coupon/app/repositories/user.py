from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from app.models import User, Redemption
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, CouponCreate, RedemptionCreate


class UserRepository:
    async def create(self, db: AsyncSession, user_data: UserCreate) -> User:
        user = User(
            name=user_data.name
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_by_id(self, db: AsyncSession, user_id: int) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_for_update(self, db: AsyncSession, user_id: int) -> User:
        result = await db.execute(select(User).where(User.id == user_id).with_for_update())
        return result.scalar_one_or_none()

    async def get_user_redemptions(self, db: AsyncSession, user_id: int):
        result = await db.execute(select(User).options(selectinload(User.redemptions)).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_users_above_average_redemptions(self, db: AsyncSession):
        user_redemption_table = (select(
            Redemption.user_id,
            func.coalesce(func.count(Redemption.id),
                          0).label('redemption_count')
        ).group_by(Redemption.user_id)
            .cte("user_redemption_table")
        )
        
        avg_redemption_count=(select(func.avg(user_redemption_table.c.redemption_count)).scalar_subquery())
        result = await db.execute(
            select(User)
            .join(user_redemption_table,user_redemption_table.c.user_id==User.id)
            .where(user_redemption_table.c.redemption_count>avg_redemption_count)
            )
        
        return result.scalars().all()


user_repository = UserRepository()
