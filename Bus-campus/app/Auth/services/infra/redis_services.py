import json
import logging
from Auth.services.infra.redis_client import get_redis, logger
from core.config import settings

import redis.asyncio as aioredis

# Blacklist de Tokens

async def blacklist_token(jti:str, expires_in_seconds:int) -> None:
    
    """
    inutile de garder un JTI révoqué après l'expiration naturelle du token 
    puisqu'il ne serait de toute façon plus accepté.
    """
    
    redis = await get_redis()
    
    key= f"auth:blacklist:{jti}"
    
    await redis.setex(name=key, time=expires_in_seconds, value="1")
    logger.info(f"Token blacklisté : jti={jti[:8]}..., TTL= {expires_in_seconds}s")
    

async def is_token_blacklisted(jti:str) -> bool:
    
    redis = await get_redis() 
    
    key= f"auth:blacklist:{jti}"
    
    result = await redis.exists(key)
    
    return result == 1
    
# cache de session utilisateur

async def cache_user_sesssion(user_id: str, user_data: dict) -> None:
    
    redis = await get_redis() 
    key= f"auth:session:{user_id}"
    await redis.setex(
        name = key,
        time = settings.session_cache_tll_seconds,
        value=json.dumps(user_data)
    
    )
    
async def get_user_session_cache(user_id: str)  -> dict | None:
    
    redis = await get_redis()
    key= f"auth:session:{user_id}"
    raw = await redis.get(key)
    
    if raw is None:
        return None
        
    return json.loads(raw)
    
 
async def invalidate_user_session(user_id:str) -> None:
     
     redis = await get_redis()
     key = f"auth:session:{user_id}"
     await redis.delete(key)
     logger.info(f"session cache invalidated: user_id={user_id[:8]}...")
     
# Rate limiting

async def increment_login_attempt(ip_adresse: str) -> int:
    
    """
    incrémente le nombre de tentatives
    de connexion pour une IP
    """  
    redis = await get_redis()
    key= f"auth:login_attempts:{ip_adresse}"
    
    current = await redis.incr(key)
    
    if current == 1:
        await redis.expire(key, settings.login_lockout_minutes *60)
        
    logger.debug("login attempt: ", current, "from IP", ip_adresse) 
    return current
    
async def get_login_attempts(ip_adresse: str) -> int:
    
    redis = await get_redis()   
    key = f"auth:login_attempts:{ip_adresse}" 
    value = await redis.get(key) 
    return int(value) if value is not None else 0
    
async def reset_login_attempts(ip_adresse:str) -> None:
    
    redis = await get_redis()
    key = f"auth:login_attempts:{ip_adresse}"
    
    await redis.delete(key)


# blacklist de refresh token

async def blacklist_refresh_token(jti:str) -> None:
    
    redis = await get_redis()
    
    key = f"auth:refresh_blacklist:{jti}"
    TTL = settings.jwt_refresh_token_expire * 24 * 3600
    await redis.setex(name=key, time=TTL, value= "1")
 
    
async def is_refresh_token_blacklisted(jti: str) -> bool:
     
     redis = await get_redis()
     key = f"auth:refresh_blacklist:{jti}"
     return await redis.exists(key) == 1
     
    
        
     