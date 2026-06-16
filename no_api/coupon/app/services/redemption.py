from app.models import Redemption, Coupon, User
from app.schemas import RedemptionCreate, UserCreate, CouponCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user import user_service
from app.services.coupon import coupon_service
from app.repositories.redemption import redemption_repository
from app.repositories.coupon import coupon_repository

class RedemptionService:
    async def redeem_coupon(self,db:AsyncSession,user_id:int,coupon_code:str)->Redemption:
        async with db.begin():
            # check user exists
            user=await user_service.get_by_id(db,user_id)
            
            # check coupon exists
            coupon= await coupon_service.get_by_code(db,coupon_code)

            # check if redemption exists
            redemption=await redemption_repository.get_by_id(db,user_id=user_id,coupon_id=coupon.id)
            # if redemption exists dont make new
            if redemption:
                raise ValueError("status_code=400, detail=Coupon already redeemed")
            
            # create a redemption record for the user
            redemption=await redemption_repository.create(db,RedemptionCreate(user_id=user_id,coupon_id=coupon.id))
            
            # update the redemptions left for the coupon
            coupon=await coupon_repository.get_for_update(db,coupon.id)
            coupon.remaining_redemptions-=1
            
            return redemption
            
            
            
redemption_service=RedemptionService()