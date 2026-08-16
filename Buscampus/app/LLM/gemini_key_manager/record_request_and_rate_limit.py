import logging
import time 
from LLM.gemini_key_manager._load_and_select_key import *


async def record_request(key_label:str) -> None:
    
    if not key_label or not key_label.strip():
        logger.warning("record request: key_label vide")
        return
        
    try:
        redis = await _get_redis()
        counter_key = f"gemini:key:{key_label}:request_this_minute"
        count = await redis.incr(counter_key)
        
        if count == 1:
            await redis.expire(counter_key, COUNTER_TTL_SECONDS)
            
    except Exception as err:
        logger.info(f"record request: Redis error: {error}")   
        
async def mark_rate_limited(key_label: str)   -> None:
    
    """
    Marque une clé comme rate-limité après qu'une réponse 
    HTTP 429 de gemini survienne.
    
    la clé sera donc indisponible durant le temps mis pour 
    RATE_LIMIT_COOLDOWN_SECONDS
    """          
        
    if not key_label or not key_label.strip():
        logger.warning("mark_rate_limited : key_label vide")
        return 
        
    try:
        redis = await _get_redis()   
        cooldown_key = f"gemini:key:{key_label}:rate_limited_until" 
        cooldown_until = time.time() + RATE_LIMIT_COOLDOWN_SECONDS
        
        await redis.set(cooldown_key, str(cooldown_until), ex=RATE_LIMIT_COOLDOWN_SECONDS + 5)
        logger.warning(
                 f"mark_rate_limited : clé {key_label} en cooldown"
                 f"pour {RATE_LIMIT_COOLDOWN_SECONDS}s"
        )
        
        
    except Exception as err:
        logger.error(f"mark_rate_limited : Redis error : {error}")    
        
        
        
        