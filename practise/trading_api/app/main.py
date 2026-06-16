from fastapi import FastAPI,HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app.logger import setup_logger
from app.config import get_settings
import time

settings=get_settings()
logger=setup_logger(__name__)

app=FastAPI(title=settings.app_name,description=settings.app_name,version=settings.app_version)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.middleware('http')
async def log_requests(request:Request,call_next):
    start_time=time.perf_counter()
    logger.info(f"handling Request| {request.method} {request.url.path}")
    response=await call_next(request)
    duration=time.perf_counter()-start_time
    
    logger.info(f"Completed Request | {request.method} {request.url.path}"
                f"status={response.status_code} duration={duration}")
    return response

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request:Request, exc:RequestValidationError):
    logger.warning(f"Validation Error | {request.method} {request.url.path} error={jsonable_encoder(exc.errors())}")
    raise JSONResponse(
        status_code=422,
        detail=f"error=Validation Error  error={jsonable_encoder(exc.errors())}"
    )
    
@app.exception_handler(Exception)
async def handle_general_error(request:Request, exc:Exception):
    logger.warning(f"Unexpected Error | {request.method} {request.url.path} error={str(exc)}")
    raise JSONResponse(
        status_code=500,
        detail=f"error=Internal Server Error  error={str(exc)}"
    )

app.include_router()

@app.get('/')
async def check_health():
    return {"status":"ok",
            "detail":"working perfectly"}