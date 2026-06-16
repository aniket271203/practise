from fastapi import FastAPI, Request
from apis.trader_api.app.config import get_settings
from apis.trader_api.app.database import Base, engine
import time
from apis.trader_api.app.logger import setup_logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from apis.trader_api.app.routers.trader import trader_router
from apis.trader_api.app.routers.trade import trade_router
from apis.trader_api.app.routers.position import position_router

logger=setup_logger(__name__)

settings=get_settings()

app=FastAPI(title=settings.app_name, description="Trader API NK", version=settings.app_version)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.middleware("http")
async def log_request(request:Request,call_next):
    start_time=time.perf_counter()
    logger.info(f"Handling Request | {request.method} {request.url.path}")
    response=await call_next(request)
    
    duration=time.perf_counter()-start_time
    logger.info(f"Completed Request | {request.method} {request.url.path}"
                f"status={response.status_code} duration={duration}")
    return response

@app.exception_handler(RequestValidationError)
async def handle_request_error(request:Request, exc: RequestValidationError):
    logger.warning(f"Validation error | {request.url.path} error={jsonable_encoder(exc.errors())}")
    return JSONResponse(
        status_code=422,
        content=f"error=Validation Error detail={jsonable_encoder(exc.errors())}"
    )
  
@app.exception_handler(Exception)
async def handle_general_error(request:Request, exc: Exception):
    logger.warning(f"Unexpected error | {request.url.path} error={str(exc)}")
    return JSONResponse(
        status_code=500,
        content=f"error= Internal Server Error detail={str(exc)}"
    )  
    
app.include_router(trader_router)
app.include_router(trade_router)
app.include_router(position_router)

@app.get('/')
async def check_health():
    return {
        "status":"ok",
        "detail":"works perfectly"
    }