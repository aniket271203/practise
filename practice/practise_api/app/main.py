from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from apis.practise_api.app.logger import setup_logger
from apis.practise_api.app.database import Base, engine
from apis.practise_api.app.config import get_settings
import time
from app.routers import router

logger=setup_logger(__name__)

settings=get_settings()

app=FastAPI(title=settings.app_name, description="Trade API NK",version=settings.app_version)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request:Request, exc: RequestValidationError):
    logger.warning(f"Validation Error | {request.method} {request.url.path} error={jsonable_encoder(exc.errors())}")
    raise JSONResponse(
        status_code=429,
        content={"error":"validation Error", "detail":jsonable_encoder(exc.errors())}
    )
    
@app.exception_handler(Exception)
async def handle_validation_error(request:Request, exc: Exception):
    logger.warning(f"Unexpected Error | {request.method} {request.url.path} error={str(exc)}")
    raise JSONResponse(
        status_code=500,
        content={"error":"Unexpected Error", "detail":str(exc)}
    )

@app.middleware("http")
async def log_request(request:Request, call_next):
    start_time=time.perf_counter()
    logger.info(f"Handling request | {request.method} {request.url.path}")
    response=await call_next(request)
    
    duration=time.perf_counter()-start_time
    logger.info(f"Request Completed | {request.method} {request.url.path}"
                f"status={response.status_code} duration={duration}")
    return response


# app.include_router(router)

@app.get("/")
async def check_health():
    return {"status":"ok", "detail":"works perfectly"}