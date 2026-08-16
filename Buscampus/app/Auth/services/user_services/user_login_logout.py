
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from Auth.services.infra.redis_client import logger
from Auth.services.infra.redis_services import (
    cache_user_sesssion,
    invalidate_user_session,
    increment_login_attempt,
    get_login_attempts,
    reset_login_attempts,
    blacklist_token,
)

from Auth.services.jwt_services import (
    create_refresh_token,
    create_access_token,
)

from Auth.schemas import TokenResponse
from core.config import settings
from Auth.services.password_service import verify_password
from Auth.services.user_services.AuthError import AuthError
from Auth.models import User, RefreshToken



async def login_user(
    email: str,
    password: str,
    ip_adresse: str,
    session: AsyncSession) -> TokenResponse:
    
    attempts = await get_login_attempts(ip_adresse)
    if attempts >= settings.login_max_attempts:
        raise AuthError(
            f"Trop de tentatives, réessayez dans "
            f'{settings.login_lockout_minutes} minutes',
            f"Rate limited IP: {ip_adresse}, attempts = {attempts}"
        )
        
    result = await session.execute(
        select(User).where(User.email == email)
    )
    
    user = result.scalar_one_or_none()
    
    if user is None or not verify_password(plain_password=password, hashed_password=user.hashed_password):
        await increment_login_attempt(ip_adresse)
        raise AuthError(
            "Email ou mot de passe incorrect",
            f"failed login for email={email}, ip={ip_adresse}"
        )
        
    if not user.is_active:
        raise AuthError(
            "Ce compte est désactivé ",
            f"failed login for email={email}, ip={ip_adresse}"
        )
        
        
    await reset_login_attempts(ip_adresse)
    
    access_token, access_jti, access_expires_at = create_access_token(
        user_id=str(user.id),
        email=user.email
    )
    
    refresh_token_str, refresh_token_jti, refresh_expires_at = create_refresh_token(
        user_id=str(user.id)
    )
    
    import hashlib
    
    refresh_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
    
    from datetime import datetime, timezone
    
    ip_str = str(ip_adresse) if ip_adresse else None
    
    refresh_record = RefreshToken(
        user_id= user.id,
        token_hash = refresh_hash,
        expires_at = refresh_expires_at,
        ip_adresse= ip_str
        
    )
    
    session.add(refresh_record)
    await session.flush()
    
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    }
    
    await cache_user_sesssion(str(user.id), user_data)
    
    logger.info(f"user logged in: id = {user.id}, ip={ip_adresse}")
    
    expires_in = settings.jwt_access_token_expire_minutes * 60
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=expires_in
    )
    
    

async def logout_user(jti: str, expires_in_seconds: int, user_id: str) -> None:
    
    await blacklist_token(jti, expires_in_seconds)
    await invalidate_user_session(user_id)
    logger.info(f"User logged out: user_id={user_id[:8]}..., jti={jti[:8]}...")



