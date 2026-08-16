import logging

from fastapi import APIRouter,  Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from Auth.services.dependencies import require_jwt_auth
from Auth.schemas import (
    ApiKeyCreateResponse,
    ApiKeyCreateRequest,
    ApiKeyListItem,
    AuthenticatedUser
    
    
)
from Auth.services.user_services.AuthError import AuthError

from Auth.services.user_services.API_KEYS import create_api_keys, list_api_keys, revoke_api_key



from core.database import get_session

logger = logging.getLogger("auth.router")
router = APIRouter(prefix="/auth",tags=["Authentification"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/api-keys", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_key(
    body: ApiKeyCreateRequest,
    current_user: AuthenticatedUser = Depends(require_jwt_auth),
    session: AsyncSession = Depends(get_session),
): 
    try:        
        return await create_api_keys(str(current_user.id), body, session)    
    except AuthError as error:        
        raise HTTPException(            
            status_code=status.HTTP_400_BAD_REQUEST,            
            detail=error.public_message      
            )



@router.get("/api-keys", response_model=list[ApiKeyListItem])
async def get_keys(
    current_user: AuthenticatedUser = Depends(require_jwt_auth), 
    session: AsyncSession = Depends(get_session)
    ):
    keys = await list_api_keys(current_user.id, session)
    return keys or [] 
    
@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_key(    
    key_id: str,    
    current_user: AuthenticatedUser = Depends(require_jwt_auth),    
    session: AsyncSession = Depends(get_session)
    ):    
    try:        
        await revoke_api_key(key_id, current_user.id, session)   
    except AuthError as error:        
            raise HTTPException(            
                status_code=status.HTTP_404_NOT_FOUND,            
                detail=error.public_message    
            )
