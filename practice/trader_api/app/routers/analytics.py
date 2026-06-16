from fastapi import APIRouter,Depends
from apis.trader_api.app.database import get_db
from apis.trader_api.app.ratelimiter import check_rate_limit
from apis.trader_api.app.auth import verify_api_key
# from app.schemas import 
from sqlalchemy.ext.asyncio import AsyncSession

analytics_router=APIRouter(prefix='/portfolio', tags=['portfolio'],dependencies=[Depends(check_rate_limit),Depends(verify_api_key)])



