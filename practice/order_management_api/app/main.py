from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from apis.order_management_api.app.logger import setup_logger
from apis.order_management_api.app.config import get_settings
from apis.order_management_api.app.database import Base, engine
import time
from apis.order_management_api.app.routers.orders import router
from apis.order_management_api.app.routers.products import product_router

settings=get_settings()

logger= setup_logger(__name__)

app=FastAPI(title=settings.app_name, description="order management API", version=settings.app_version)

@app.on_event("startup")
async def start_up():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.middleware("http")
async def log_requests(request:Request, call_next):
    start_time=time.perf_counter()
    logger.info(f"Handling request | {request.method} {request.url.path}")
    response=await call_next(request)
    
    duration=time.perf_counter()-start_time
    logger.info(f"Completed request | {request.method} {request.url.path}"
                f"status={response.status_code} duration={duration}")
    return response

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request:Request, exc: RequestValidationError):
    logger.warning(f"Validation Error | {request.url.path} error={jsonable_encoder(exc.errors())}")
    return JSONResponse(
        status_code=422,
        content={"error":"Validation Error",  "detail":jsonable_encoder(exc.errors())}
    )
    
@app.exception_handler(Exception)
async def handle_general_error(request:Request, exc: Exception):
    logger.warning(f"Unexpected Error | {request.url.path} error={str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error":"Internal server Error",  "detail":str(exc)}
    )
    
app.include_router(router)
app.include_router(product_router)

@app.get("/")
async def check_health():
    return {
        "status":"ok",
        "detail":"Runs perfectly"
    }