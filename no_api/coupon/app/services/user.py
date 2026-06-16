from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Coupon, User, Redemption
from app.schemas import UserCreate
from app.repositories.user import user_repository


class UserService:
    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        user = await user_repository.create(db, user_data)
        return user

    async def get_by_id(self, db: AsyncSession, user_id: int) -> User:
        user = await user_repository.get_by_id(db, user_id)
        if not user:
            raise ValueError("status_code=404, detail=User Not Found")
        return user
    
    async def get_users_above_average_redemptions(self,db:AsyncSession):
        users=await user_repository.get_users_above_average_redemptions(db)
        return users

    async def get_user_redemptions(self, db: AsyncSession, user_id: int):
        user=await self.get_by_id(db,user_id)
        users=await user_repository.get_user_redemptions(db,user_id)
        return users

user_service = UserService()
