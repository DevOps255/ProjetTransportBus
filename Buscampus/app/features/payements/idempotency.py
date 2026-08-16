import hashlib
import logging

from _redis_client import _get_redis

from core.config import settings

logger = logging.getLogger("payment.idempotency")

def _hash_sms_text(sms_text: str) -> str:
    
    """
    SHA256 du texte brut du SMS normalisé    
    Utilisé comme clé du niveau 1 d'idempotence.
    
    C'est juste pour garantir que le même SMS 
    reçu avec des espaces inutile ou un truc différent 
    produit la même clé redis.
    """
    
    if sms_text is None:
        raise ValueError("_hash_sms_text : sms_text ne peut pas être None")
    
    normalized = sms_text.strip().lower()
    
    if not normalized:
        raise ValueError("_hash_sms_text : sms_text vide après normalisation")
        
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    

def _normalize_reference(reference: str) -> str:
    
    """
    Normalise une référence de transaction 
    pour l'idempotency    de niveau 2.
    """
    
    if reference is None:
        raise ValueError("_normalize_reference : reference ne peut pas être None)
        
   normalized = reference.strip().upper() 
   
   if not normalized:
       raise ValueError("_normalize_reference : référence vide après normalisation")
       
   return normalized
   

async def claim_sms_level1(sms_text:str) ->  tuple[bool, str]:
    
    """
    Idempotence de NIVEAU 1 basée sur le hash du SMS brut.  
    on veux empêcher que le même SMS de paiement soit traité plusieurs fois.
    
    On renvoi (True, sms_hash) si la clé a été réclamée avec succès.    
    On renvoi (False, sms_hash) si ce SMS a déjà été vu.    
    Le sms_hash est retourné pour permettre à la couche appelante    
    de libérer la clé si le traitement échoue
    """
    
    sms_hash = _hash_sms_text(sms_text)
    redis = await _get_redis()
    
    key = f"payment:idempotency:sms:{sms_hash}"
    
    was_set = await redis.set(
        name=key,
        value= "processed",
        nx=True,
        ex=settings.idempotency_ttl_seconds * 2
        
    )
    
    claimed = was_set is True
    
    if not claimed:
        logger.info(
            f"Level-1 idempotency hit : sms_hash={sms_hash[:16]}..."
        )
        
        
	return claimed, sms_hash
    
async def claim_reference_level2(reference: str)  ->  bool:
    
    """
    Idempotence de NIVEAU 2 basée sur la référence de transaction.    
    ceci sera exécuté après le parsing de gemini ou Mistral apres que la 
    référence sera extraite
    
    Contrairement au niveau 1, on ne retourne pas de clé à libérer 
    parce que si la référence est dans Redis, c'est définitif donc ette transaction   
    a déjà ajouté de l'argent au portfeuille. 
    """   
    normalized = _normalize_reference(reference)
    redis = _get_redis()
    key =  f"payment:idempotency:ref:{normalized}"
    
    was_set = await redis.set(
        name=key,
        value= "processed",
        nx=True,
        ex=settings.idempotency_ttl_seconds * 2
    )
    claimed = was_set is True
    if not claimed:
        logger.info(
            f"Level-2 idempotency hit : reference={reference[:8]}..."
        )
    return claimed
    
async def release_sms_level1(sms_hash:str) -> str:
    
    """
     on libère la clé d'idempotence de niveau 1.    
     cette fonction sera appellée si le traitement échoue APRÈS la réclamation du niveau 1    (timeout, erreur base de données) 
     pour permettre un retry légitime du SMS.    
     
     par contre on ne libère JAMAIS le niveau 2 (référence de transaction). C'est même évident
     
     dès une qu'une référence de transaction est réussie, on la garde pour toujours    
     jusqu'à expiration du TTL.
    """
    
    if not sms_hash:
        logger.info(
            "release_sms_level1 called with empty sms_hash "
            "cannot release idempotency key"
        )
        return 
        
    redis = await _get_redis()    
    key = f"payment:idempotency:sms:{sms_hash}"
    deleted = await redis.delete(key)
    
    if deleted:
        logger.info(f"Level-1 idempotency key released : {sms_hash[:16]}...)"
        
    else:
        logger.warning(
            f"Level-1 idempotency key not found during release "            
            f"(already expired?) : {sms_hash[:16]}..."
        )
            

