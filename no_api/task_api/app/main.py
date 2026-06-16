# from fastapi import FastAPI, HTTPException, Request
# from fastapi.exceptions import RequestValidationError
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse
# from app.logger import setup_logger
# from app.config import get_settings
# from app.database import engine, Base
# import time

# settings = get_settings()

# logger = setup_logger(__name__)

# app = FastAPI(title=settings.app_name,
#               description=settings.app_name, version=settings.app_version)


# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# @app.middleware('http')
# async def log_request(request: Request, call_next):
#     start_time = time.perf_counter()
#     logger.info(f"Handling Request | {request.method} {request.url.path}")
#     response = await call_next(request)
#     duration = time.perf_counter()-start_time

#     logger.info(f"Handled Request | {request.method} {request.url.path}"
#                 f"status={response.status_code} duration={duration}")

#     return response

# @app.exception_handler(RequestValidationError)
# async def handle_validation_error(request:Request,exc:RequestValidationError):
#     logger.warning(f"Validation Error | {request.method} {request.url.path} error={jsonable_encoder(exc.errors())}")
#     return JSONResponse(
#         status_code=422,
#         detail=f"error=Validation Error, detail={jsonable_encoder(exc.errors())}"
#     )

# @app.exception_handler(Exception)
# async def handle_general_error(request:Request,exc:Exception):
#     logger.warning(f"Unexpected Error | {request.method} {request.url.path} error={str(exc)}")
#     return JSONResponse(
#         status_code=500,
#         detail=f"error=Internal Server Error, detail={str(exc)}"
#     )   

# app.include_router()


# @app.get('/')
# async def check_health():
#     return {
#         "status": "ok",
#         "detail": "Works fine"
#     }

import asyncio
from app.database import engine,AsyncLocalSession,Base

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def main():
    await create_tables()
    
    async with AsyncLocalSession() as db:
        pass
    
if __name__=="__main__":
    asyncio.run(main())