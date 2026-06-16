from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from apis.trading_api_1.app.logger import setup_logger
from apis.trading_api_1.app.routers import router
import time
from apis.trading_api_1.app.database import Base,engine

logger=setup_logger(__name__)

Base.metadata.create_all(bind=engine)

app=FastAPI(title="Trading API", description="practise API",version="1.0.0")

@app.middleware("http")
async def log_request(request:Request, call_next):
    logger.info(f"Started Request | {request.method} {request.url.path}")
    start_time=time.perf_counter()
    response=await call_next(request)
    duration=time.perf_counter()-start_time
    logger.info(f"Request Completed| status_code={response.status_code} | {request.url.path} | duration={duration}")
    return response

@app.exception_handler(RequestValidationError)
def request_validation_exception(request: Request, exc: RequestValidationError):
    logger.info(f"Validation Error | request = {request.url.path} | errors = {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error":"Validation error", "detail":exc.errors()}
    )

@app.exception_handler(Exception)
def general_exception(request:Request,exc:Exception):
    logger.info(f"Unexpected Error | request={request.url.path} | error={str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error":"Internal Server Error", "detail":str(exc)}
    )


app.include_router(router)
@app.get('/')
def check_health():
    return {"message":"API working fine"}