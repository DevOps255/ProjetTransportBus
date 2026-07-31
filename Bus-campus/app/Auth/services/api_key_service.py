import hashlib
import secrets
from datetime import datetime, timezone

from core.config import settings
from Auth.services.password_service import hash_password, verify_password


def generate_api_key() ->  tuple[str, str, str]:
    
    random_bytes = str(secrets.token_urlsafe(settings.api_key_key_length))
    
    raw_key =  f"{settings.api_key_prefix}{random_bytes}"
    
    key_prefix= random_bytes[:8]
    
    hashed_key= hash_password(str(raw_key))
    
    return key_prefix, raw_key, hashed_key
    
    
def verify_api_key(raw_key: str, hashed_key: str ) -> bool:
    
    return verify_password(raw_key, hashed_key)

def compute_key_lookup_prefix(raw_key: str) -> bool:
    
    """
    on essai d'extraire le préfixe de la clé brute pour 
    rechercher dans la base de donnée, mais le problème c'est 
    qu'on a hashé la clé avec bcrypt, on peut pas faire de 
    SELECT, la même clé produit un hash différent à chaque fois
    
    
    alors la solution est de stocker le key_prefix et on fait un 
    SELECT * FROM api_keys WHERE key_prefix = ? AND is_active = true
    
    on vérifie chaque  hash bcrypt ensuite, mais bon! 
    
    c'est possible que ça retourner plusieurs clé (collision de préfixe)
    
    Avec 218 Milliards de combinaisons possible, les collisions seront rares
    
    
    """
    
    prefix_length= len(settings.api_key_prefix)
    
    return raw_key[prefix_length: prefix_length + 8]
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    