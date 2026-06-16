from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from apis.portfolio_api.app.database import Base, engine
from apis.portfolio_api.app.routers import router
from apis.portfolio_api.app.logger import setup_logger
import time
from fastapi.encoders import jsonable_encoder
from apis.portfolio_api.app.config import get_settings

settings=get_settings()

logger=setup_logger(__name__)

# Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name, description=settings.app_name, version=settings.app_version)

@app.on_event("startup")
async def start_up():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("ALl DB Tables Created")
    

@app.middleware("http")
async def log_requests(request:Request,call_next):
    logger.info(f"handling Request | {request.method} {request.url.path}")
    start_time=time.perf_counter()
    response=await call_next(request)
    duration=time.perf_counter()-start_time
    logger.info(f"request completed | request={request.url.path} status_code={response.status_code} duration={duration}")
    return response

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error | {request.method} {request.url.path}| error={jsonable_encoder(exc.errors())}")
    return JSONResponse(
        status_code=422,
        content={"error":"Validation error", "detail":jsonable_encoder(exc.errors())}
    )
    
@app.exception_handler(Exception)
async def handle_general_exception(request:Request,exc:Exception):
    logger.warning(f"Unexpected error | {request.method} {request.url.path}| error={str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error":"Internal server Error", "detail":str(exc)}
    )
    
app.include_router(router)

@app.get("/")
async def health_check():
    return {"status":"ok","message":"everythign works perfectly"}