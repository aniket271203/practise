from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from apis.trading_api.app.routers import router
from apis.trading_api.app.database import engine, Base
import time
from apis.trading_api.app.logger import setup_logger
from apis.trading_api.app.config import get_settings
from fastapi.encoders import jsonable_encoder

settings=get_settings()

logger=setup_logger(__name__)

# creates all tables on startup
# Base.metadata.create_all(bind=engine)

app=FastAPI(title=settings.app_name, description=settings.app_name, version=settings.app_version)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Created all DB Tables")

@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time=time.perf_counter()
    logger.info(f"Request started | {request.method} {request.url.path}")
    response= await call_next(request)

    duration=time.perf_counter()-start_time
    logger.info(f"request Completed | {request.method} {request.url.path}"
                f"status={response.status_code} duration={duration}")
    return response

@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error | {request.method} {request.url.path} | {jsonable_encoder(exc.errors())}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details":jsonable_encoder(exc.errors())}
    )

@app.exception_handler(Exception)
async def handle_general_exception(request: Request, exc: Exception):
    logger.warning(f"Enexpected Error | {request.url.path} | {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error":"internal server error", "details":str(exc)}
    )
    
app.include_router(router)

@app.get("/")
async def check_health():
    return {"status":"ok","message":"Trading API is working"}
