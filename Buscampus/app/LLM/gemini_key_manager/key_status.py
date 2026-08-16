import logging
import time 
from _redis_client import _get_redis
from LLM.gemini_key_manager.NoAvailaibleGeminiKeyError import NoAvailableGeminiKeyError
from LLM.gemini_key_manager._load_and_select_key import _load_keys

async def get_all_key_status() -> list[dict]:
    
    all_keys = _load_keys()
    
    if not all_keys:
        return []
    
    try:
        redis = _get_redis()
    except Exception:
        for key in all_keys:
            return {
                "label": key.label,
                "project_name":key.project_name,
                "status": "unknown",
                "request_this_minute": None
            }
    
    statuses = []
    now = time.time()
    
    
    for key in all_keys:
        cooldown_raw = await redis.get(f"gemini:key:{key.label}:rate_limited_until")
        count_raw = await redis.get(f"gemini:key:{key.label}:requests_this_minute")
        
        is_rate_limited = (
            cooldown_raw is not None and now < float(cooldown_raw)
        )
        statuses.append({
            "label": key.label,
            "project": key.project_name,
            "status": "rate_limited" if  is_rate_limited else "available",
            "request_this_minute": int(count_raw) if count_raw else 0
        })
        
    return statuses
    
    
    
    
    
    
    
      