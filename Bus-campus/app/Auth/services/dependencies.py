import logging
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from Auth.schemas import AuthenticatedUser
from Auth.services.jwt_services import TokenError, decode_access_token
from Auth.services.infra.redis_services import (
    get_user_session_cache,
    cache_user_sesssion,
    is_token_blacklisted
)
 
from Auth.services.user_services.API_KEYS import verify_api_from_request

from core.database import get_session
from core.config import settings

logger = logging.getLogger("auth.dependencies")

bearer_schema = HTTPBearer(auto_error=False)

async def _load_user(user_id: str, session: AsyncSession) -> dict | None:
    
    from Auth.models import User
    import uuid
    
    user = await session.get(User, uuid.UUID(user_id))
    
    if user is None or not user.is_active:
        
        return None
        
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    }
    
    await cache_user_sesssion(user_id, user_data)
    return user_data


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_schema),
    session: AsyncSession = Depends(get_session)) -> AuthenticatedUser:
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Une Authentification est requise",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )
    
    token = credentials.credentials
    
    if token.startswith(settings.api_key_prefix):
        user = await verify_api_from_request(token, session)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key invalide ou révoqué",
                headers={
                    "WWW-Authenticate": "Bearer"
                }
            )
        logger.debug(f"API key Auth success: user_id={str(user.id)[:8]}...")    
        
        return AuthenticatedUser(
            id= str(user.id),
            email= user.email,
            is_active= user.is_active,
            auth_method = "api-key"
        )
    try:
        
        payload = decode_access_token(token)    
    except TokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )
        
    jti = payload.get("jti")    
    user_id = payload.get("sub")    
    
    if jti and await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token révoqué",
            headers={
                "WWW-Authenticate": "Bearer"
            }
            
        )
    
    user_data = await get_user_session_cache(user_id) 
    
    if user_data is None:
        user_data = await _load_user(user_id, session)
        
    if user_data is None or not user_data.get("is_active"):
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="compte introuvable ou désactivé"
        )
         
    logger.debug(f"JWT auth success : user_id={user_id[:8]}...")
    
    return AuthenticatedUser(
        id=user_id, 
        email=user_data["email"],
        is_active = user_data["is_active"],
        auth_method= "jwt"
    )


async def require_jwt_auth(current_user: AuthenticatedUser = Depends(get_current_user))-> AuthenticatedUser:
    
    if current_user.auth_method != "jwt":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="cette action nécessite une authentification jwt"
        )
    return current_user    
    
    


