from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from apis.task_api.app.database import engine, Base
from apis.task_api.app.routers import router
from apis.task_api.app.logger import setup_logger
import time 
from apis.task_api.app.config import get_settings

settings=get_settings()

logger=setup_logger(__name__)

app=FastAPI(title=settings.app_name, description="tasks API",version=settings.app_version)

@app.middleware("http")
async def log_request(request:Request, call_next):
    start_time=time.perf_counter()
    logger.info(f"Handling Request | {request.method} {request.url.path}")
    response=await call_next(request)
    
    duration=time.perf_counter()-start_time
    logger.info(f"Completed Request | {request.method} {request.url.path}"
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
    logger.warning(f"Unexpected Error | {request.url.path} | {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error":"internal server error", "details":str(exc)}
    )
    

app.include_router(router)

@app.get('/')
async def check_health():
    return {"status":"ok", "message":"the system runs perfectly"}