from apis.trading_api.app.config import get_settings
from fastapi import Security,HTTPException, status
from fastapi.security import APIKeyHeader
from apis.trading_api.app.logger import setup_logger

logger=setup_logger(__name__)

settings=get_settings()

api_key_header=APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key=Security(api_key_header)):
    if not api_key:
        logger.warning("request missing APi key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request missing API key"
        )
    if api_key!=settings.api_key:
        logger.warning(f"Invalid API key attempt | key={api_key[:6]}....")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid API key "
        )
    return api_key
    