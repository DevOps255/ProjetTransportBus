import uuid
from datetime import datetime, timezone, timedelta
from jose import ExpiredSignatureError, JWTError, jwt
from core.config import settings


class TokenError(Exception):
    pass
    
    
def _utcnow() -> datetime:
    
    return datetime.now(tz=timezone.utc)    
    
def create_access_token(user_id:str, email:str) -> tuple[str, str, datetime]:
     
     jti = str(uuid.uuid4())
     expires_at= _utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
     
     payload = {
         "sub": user_id,
         "email": email,
         "type": "access",
         "jti": jti,
         "issued_at": int(_utcnow().timestamp()),
         "exp": int(expires_at.timestamp())
         
     }
     
     token= jwt.encode(
         payload, 
         settings.JWT_SECRET_KEY, 
         algorithm=settings.jwt_algorithm
         )
     return token, jti, expires_at
     
def create_refresh_token(user_id:str)->tuple[str, str, datetime]:
    
    jti = str(uuid.uuid4())   
    expires_at= _utcnow() + timedelta(days=settings.jwt_refresh_token_expire)
    
    payload={
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "issued_at": int(_utcnow().timestamp()),
        "expires_at": int(expires_at.timestamp())
    }
    
    token = jwt.encode(
        payload, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.jwt_algorithm
    )
    
    return token, jti, expires_at
    
def decode_access_token(token:str) -> dict:
    
    try:
        
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.jwt_algorithm]
        )
    
    except ExpiredSignatureError:
        raise TokenError("Token expiré")
    except JWTError:
        raise TokenError("Token invalide ")
        
    if payload.get("type") != "access":
        raise TokenError("type de Token incorrect")
    return payload
    
            
def decode_refresh_token(token: str) -> dict:
    
    try:
        
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.jwt_algorithm]
        )
        
    except ExpiredSignatureError:
        raise TokenError("Token expiré")
    except JWTError:
        raise TokenError("Token invalide ")
        
    if payload.get("type") != "refresh":
        raise TokenError("type de Token incorrect")
    return payload
    
          
    
    
 