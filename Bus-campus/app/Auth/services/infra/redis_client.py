
import logging

import redis.asyncio as aioredis
from core.config import settings


logger = logging.getLogger("auth.redis")
_redis_client: aioredis.Redis | None = None

async def get_redis() -> aioredis.Redis:
    
    global _redis_client
    if _redis_client is None:
        _redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding= "utf-8",
            max_connections=20
            
        )
        
    return _redis_client
