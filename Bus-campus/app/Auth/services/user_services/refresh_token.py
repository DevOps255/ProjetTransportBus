from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from Auth.services.infra.redis_client import logger
from Auth.services.infra.redis_services import (
    blacklist_refresh_token,
    is_refresh_token_blacklisted
)

from Auth.services.jwt_services import (
    create_refresh_token,
    create_access_token,
    decode_refresh_token,
    TokenError
)

from Auth.schemas import TokenResponse
from core.config import settings
from Auth.services.user_services.AuthError import AuthError
from Auth.models import User, RefreshToken



async def refresh_token(refresh_token_str: str, session: AsyncSession) -> TokenResponse:
    
    try:
        
        payload = decode_refresh_token(refresh_token_str)
        
    except TokenError as error:
        
        raise AuthError("Refresh Token invalide", str(error))
        
        
    jti = payload.get("jti")
    user_id = payload.get("sub")
    
    if await is_refresh_token_blacklisted(jti):
        raise AuthError(
            "Refresh Token révoqué",
            f"blacklisted refresh token used: jti= {jti}"
        )
        
    import hashlib
    
    token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
    
    result = await session.execute(
        select(RefreshToken)
        .where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False
        )
    )
    refresh_record = result.scalar_one_or_none()
    
    if refresh_record is None:
        raise AuthError(
            "Refresh token invalide",
            f"refresh token not found in DB: hash={token_hash[:16]}"
        )
    user = await session.get(User, refresh_record.user_id)
    
    if user is None or not user.is_active:
        
        raise AuthError("compte introuvable ou désactivé")
        
    await blacklist_refresh_token(jti)
    
    refresh_record.is_revoked = True
    
    await session.flush()
    
    new_access_token, new_access_expires_at, new_access_jti = create_access_token(
        user_id=str(user.id),
        email=user.email
    )
    
    new_refresh_str, new_refresh_jti, new_refresh_expires_at = create_refresh_token(
        user_id=str(user.id)
    )
    
    new_hash = hashlib.sha256(new_refresh_str.encode()).hexdigest()
    
    new_refresh_record = RefreshToken(
        user_id = user.id,
        token_hash = new_hash,
        expires_at = new_refresh_expires_at
    )
    
    session.add(new_refresh_record)
    
    await session.flush()
    
    logger.info(f"Token refreshed: user_id={user.id}")
    
    return TokenResponse(
        access_token= new_access_token,
        refresh_token= new_refresh_str,
        token_type= "bearer",
        expires_in= settings.jwt_access_token_expire_minutes * 60
    )






