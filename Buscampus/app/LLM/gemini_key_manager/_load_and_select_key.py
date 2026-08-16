import logging
import time
from dataclasses import dataclass

from _redis_client import _get_redis
from core.config import settings

logger = logging.getLogger("LLM.gemini_key_manager")


REQUEST_PER_MINUTE_LIMIT = 500
RATE_LIMIT_COOLDOWN_SECONDS = 60
COUNTER_TTL_SECONDS = 65


@dataclass(frozen=True)
class GeminiKey:
    
    label: str
    api_key: str
    project_name: str
    
def _load_keys()-> list[GeminiKey]:
    
    keys: list[GeminiKey] = []
    
    raw_keys = [
        (
            "A",
            settings.gemini_key_a,
            settings.gemini_project_a
        ),(
            "B",
            settings.gemini_key_b,
            settings.gemini_project_b
        ),(
            "C",
            settings.gemini_key_c,
            settings.gemini_project_c
        )
    ]
    for label, api_key, project_name in raw_keys:
        if api_key and api_key.strip():
            keys.append(GeminiKey(
                label=label,
                api_key=api_key.strip(),
                project_name=project_name or f"project-{label.lower()}"
            ))
    return keys
             
             

    
async def select_available_key() -> GeminiKey | None:
    
    """
    On sélectionne la clé Gemini la moins chargée de requêtes
    
    Bon en fait d'abord on charge toutes les clés configurées
    
    Maintenant pour chaque clé, on vérifie qu'elle est rate-limited
    
    Si c'est le cas elle sera en temps de recharge, Ce j'appelle Cool down
    
    Ensuite, parmis les clés disponible, on vérifie celle avec le compteur 
    de requêtes le plus bas, De la repartirons de charge en quelque sorte
    
    si aucune clés n'est disponible, on retourne None
    """
    
    all_keys = _load_keys()
    
    if not all_keys:
        logger.error("select_available_key: Aucune clé gemini configurée")
        return None
    try:
        redis = await _get_redis()
    except Exception as err:
        logger.error(f"select_available_key: Redis indisponible: {err}")    
        return all_keys[0]
    
    candidates: list[tuple[GeminiKey, int]] = []
    
    for key in all_keys:
        cooldown_key = f"gemini:key:{key.label}:rate_limited_until"
        cooldown_until_raw =await redis.get(cooldown_key)
        
        if cooldown_until_raw is not None:
            cooldown_until = float(cooldown_until_raw)
            
            if time.time() < cooldown_until:
                continue
        
        counter_key = f"gemini:key:{key.label}:requests_this_minutes"        
        counter_raw = await redis.get(counter_key)
        count = int(counter_raw) if counter_raw else 0
        candidates.append((key, count))
    
    
    if not candidates:
        logger.warning("select_available_key: Toutes les clés gémini sont rate-limitées")    
        return None
        
    #on choisi la clé avec le moins de requêtes
    candidates.sort(key=lambda pair: pair[1])     
    selected_key, current_key = candidates[0]
    logger.debug(
            f"select_available_key : clé sélectionnée = {selected_key.label}
            f"(projet={selected_key.project_name}, charge={current_count})"
    )
    return selected_key





