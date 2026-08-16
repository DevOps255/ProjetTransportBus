from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128
    )
    full_name: str = Field(default="", max_length=255)
    
    
class UserLoginRequest(BaseModel):
    
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)    
    
 
class TokenResponse(BaseModel):
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
     
     
class UserResponse(BaseModel):
    
    id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
class RefreshRequest(BaseModel):
    
    refresh_token: str   
    
class ApiKeyCreateRequest(BaseModel):
    
    name: str = Field(min_length=1, max_length=100)
    
    expires_at: datetime | None = Field(default=None)
    
  
class ApiKeyCreateResponse(BaseModel):
    
    id: str
    name: str
    raw_key: str
    key_prefix: str
    expires_at: datetime | None
    created_at: datetime
    Warning: str = (
        "Copiez cette clé Maintenant. Elle ne sera plus jamais affichée"
    )
    
class  ApiKeyListItem(BaseModel):
    
    id: str
    name: str
    key_prefix: str
    is_active: bool
    expire_at: datetime | None
    last_used_at: datetime | None
    
    
class AuthenticatedUser(BaseModel):
    
    id: str
    email: str
    is_active: bool
    auth_method: str
    
     
    
    
    
    
    
    