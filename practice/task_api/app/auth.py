from fastapi import Security,HTTPException, status
from fastapi.security import APIKeyHeader
from apis.task_api.app.logger import setup_logger
from apis.task_api.app.config import get_settings

logger=setup_logger(__name__)

settings=get_settings()

api_key_header=APIKeyHeader(name="X-API-KEY",auto_error=False)

async def verify_api_key(api_key=Security(api_key_header)):
    if not api_key:
        logger.warning("Missing API Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
        
    if api_key!=settings.api_key:
        logger.warning(f"Invalid API Key | key={api_key[:6]}....")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
        
    return api_key