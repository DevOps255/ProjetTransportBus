import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from Auth.models import Apikey
from Auth.services.infra.redis_client import logger
from Auth.services.infra.redis_services import (
    blacklist_refresh_token,
    is_refresh_token_blacklisted
)
from Auth.services.api_key_service import (
    generate_api_key, 
    compute_key_lookup_prefix,
    verify_api_key
)
    
from Auth.services.jwt_services import (
    create_refresh_token,
    create_access_token,
    decode_refresh_token,
    TokenError
)

from Auth.schemas import (
    TokenResponse, 
    ApiKeyCreateRequest, 
    ApiKeyCreateResponse, 
    ApiKeyListItem,
)
from core.config import settings
from Auth.services.user_services.AuthError import AuthError
from Auth.models import User, RefreshToken



async def create_api_keys(user_id: str, request: ApiKeyCreateRequest, session: AsyncSession ) -> ApiKeyCreateResponse:
    
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    raw_key, key_prefix, hashed_key = generate_api_key()
    
    api_key = Apikey(
        user_id = user_id,
        name=request.name,
        key_prefix=key_prefix,
        hashed_key=hashed_key,
        expires_at=request.expires_at
    )
    
    session.add(api_key)
    await session.flush()
    await session.refresh(api_key)
    
    logger.info(
        f"API key created: id={api_key.id}"
        f"user_id={str(user_id)[:8]}..., prefix={key_prefix}"
    )
    if isinstance(raw_key, tuple):
        raw_key = "".join(raw_key) 
    
    return ApiKeyCreateResponse(
        id=str(api_key.id),
        name=api_key.name,
        raw_key=raw_key,
        key_prefix=str(key_prefix),
        expires_at=api_key.expires_at,
        created_at=api_key.created_at
        
    )
    

async def list_api_keys(user_id: str, session: AsyncSession) -> list[ApiKeyListItem]:
    
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    result = await session.execute(
        select(Apikey)
        .where(Apikey.user_id == user_id)
        .order_by(Apikey.created_at.desc())
    )
    keys = result.scalars().all()
    
    for k in keys:
        return ApiKeyListItem(
            id=str(k.id),
            name=k.name,
            key_prefix=k.key_prefix,
            expires_at=k.expires_at,
            last_used_at=k.last_used_at,
            created_at=k.created_at
        )


async def revoke_api_key(key_id: str, user_id: str, session: AsyncSession) -> None:
    
    import uuid as _uuid
    
    result = await session.execute(
        select(Apikey)
        .where(
            Apikey.id == _uuid.UUID(key_id),
            Apikey.user_id == _uuid.UUID(user_id)
            
        )
    )
    
    key = result.scalar_one_or_none()
    
    if key is None:
        raise AuthError(
            "clé API introuvable",
            f"API key not found: id={key_id}, user_id={user_id}"
        )
        
    key.is_active = False
    await session.flush()
    
    logger.info(f"API key revoked: id={key_id}, user_id={user_id[:8]}...")
 


async def verify_api_from_request(raw_key:str, session: AsyncSession) -> User | None:
    
    if not raw_key.startswith(settings.api_key_prefix):
        return None
        
        
    prefix = compute_key_lookup_prefix(raw_key)    
    
    result = await session.excute(
        select(Apikey)
        .where(
            Apikey.key_prefix == prefix,
            Apikey.is_active == True
        )
    )    
    
    candidates = result.scalar().all()
    
    now = datetime.now(tz=timezone.utc)
    
    for elem in candidates:
        
        if elem.expires_at is not None:
            expires = elem.expires_at
            
            if expires.tzinfo is None:
                from datetime import timezone as tz
                expires = expires.replace(tzinfo=tz.utc)
            
            if expires < now:
                continue    
                
        if verify_api_key(raw_key, elem.hashed_key):
            
            elem.last_used_at = datetime.utcnow()
            
            await session.flush()
            
            user = await session.get(User, elem.user_id)
            
            return user
        
    return None        
            
        



