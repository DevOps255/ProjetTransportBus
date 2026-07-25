from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.Auth.services.api_key_service import (
    generate_api_key,
    verify_api_key,
    compute_key_lookup_prefix
)

from app.Auth.services.infra.redis_services import(
    cache_user_sesssion,
    get_user_session_cache,
    invalidate_user_session,
    increment_login_attempt,
    get_login_attempts,
    reset_login_attempts,
    blacklist_token,
    blacklist_refresh_token,
    is_refresh_token_blacklisted
)

from app.Auth.services.jwt_services import (
    create_refresh_token,
    create_access_token,
    decode_refresh_token,
    TokenError
)

from app.Auth.schemas import TokenResponse
from app.core.config import settings
from app.Auth.services.password_service import verify_password
from app.Auth.services.user_services.AuthError import AuthError
from app.Auth.models import User



async def login_user(
    email: str,
    password:str,
    ip_adresse:str,
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
    
    



