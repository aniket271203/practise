from fastapi import FastAPI, HTTPException, Request
from apis.trading_practise_api.app.config import get_settings
from apis.trading_practise_api.app.logger import setup_logger
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from apis.trading_practise_api.app.database import engine, Base
import time

from apis.trading_practise_api.app.routers.trades import router
from apis.trading_practise_api.app.routers.traders import trader_router

settings=get_settings()
logger=setup_logger(__name__)

app=FastAPI(title=settings.app_name, description="Trading_practise", version=settings.app_version)

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
def handle_validation_error(request:Request,exc:RequestValidationError):
    logger.warning(f"Validation error | request={request.url.path} error={jsonable_encoder(exc.errors())}")
    return JSONResponse(
        status_code=422,
        content={"error":"Validation Error","detail":jsonable_encoder(exc.errors())}
    )

@app.exception_handler(Exception)
def handle_validation_error(request:Request,exc:Exception):
    logger.warning(f"Unexpected error | request={request.url.path} error={str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error":"Internal Server Error","detail":str(exc)}
    )

app.include_router(router)
app.include_router(trader_router)

@app.get('/')
async def health_checkup():
    return {"status":"ok", "detail":"the system is working"}
