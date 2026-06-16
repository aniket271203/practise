from dataclasses import dataclass
from enum import Enum


@dataclass
class UserCreate:
    name: str


@dataclass
class CouponCreate:
    code: str
    max_redemptions: int
    remaining_redemptions: int
    discount_percentage: float
    
@dataclass
class RedemptionCreate:
    user_id:int
    coupon_id:int
