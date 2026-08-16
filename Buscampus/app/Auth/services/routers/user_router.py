import logging
from datetime import timezone, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from Auth.services.dependencies import get_current_user
from Auth.schemas import (
    AuthenticatedUser,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
    UserRegisterRequest,
    RefreshRequest
)
from Auth.services.user_services.AuthError import AuthError
from Auth.services.user_services.User_register import register_user
from Auth.services.user_services.user_login_logout import login_user, logout_user
from Auth.services.user_services.refresh_token import refresh_token

from core.database import get_session

logger = logging.getLogger("auth.router")
router = APIRouter(prefix="/auth",tags=["Authentification"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(request: Request, body: UserRegisterRequest, session: AsyncSession = Depends(get_session)):
    try:
        return await register_user(body, session)
    except AuthError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error.public_message
        )
        
            
@router.post("/login", response_model= TokenResponse)
async def login(
    http_request: Request, 
    body: UserLoginRequest,
    session: AsyncSession = Depends(get_session)
):
    
    ip = http_request.client.host if http_request.client else "unknown"
    
    try:
        return await login_user(
            email=body.email,
            password=body.password,
            ip_adresse=ip,
            session=session
            
        )
        """
        De préference, utiliser ceci uniquement 
        pour les appli mobile type flutter, 
        
        Pour Les sites webs, utliser cookie HttpOnly pour éviter
        de subir une attaque XSS ou un script malveillant peut lire ces tokens.
        """
    except AuthError as error:
        
        logger.warning(f"Login failed : {error.internal_detail}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error.public_message,
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        return await refresh_token(body.refresh_token,session)
    except AuthError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err.public_message
        )    

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    from Auth.services.jwt_services import decode_access_token
    from fastapi.security import HTTPBearer
    
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer", "").strip()
    
    try:
        
        payload = decode_access_token(token)
        jti = payload.get("jti", "")
        exp = payload.get("exp", 0)
        
        from datetime import timezone as tz
        now_ts = int(datetime.now(tz=tz.utc).timestamp())
        remaining_seconds = max(0, exp-now_ts)
        
        background_tasks.add_task(
            logout_user,
            jti=jti,
            expires_in_seconds=remaining_seconds,
            user_id=current_user.id
        )
    except Exception:
        pass
            
        
@router.get("/me", response_model=UserResponse)
async def me(
    current_user: AuthenticatedUser= Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    import uuid
    from Auth.models import User
    
    user = await session.get(User, uuid.UUID(current_user.id) )
    if user is None:
        raise HTTPException(
            status_code=404, 
            detail="Utilisateur introuvable"
        )
    return UserResponse(
        id=str(user.id),        
        email=user.email,        
        full_name=user.full_name,        
        is_active=user.is_active,        
        is_verified=user.is_verified,        
        created_at=user.created_at
    )    

