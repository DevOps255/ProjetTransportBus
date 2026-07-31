import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from Auth.models import User
from Auth.services.password_service import hash_password


from Auth.schemas import(
    UserRegisterRequest,
    UserResponse
)
from Auth.services.user_services.AuthError import AuthError



logger = logging.getLogger("Auth.user")




async def register_user(request:UserRegisterRequest, session:AsyncSession) -> UserResponse:
    
    existing = await session.execute(
        select(User)
        .where(User.email == request.email)
    ) 
    
    if existing.scalar_one_or_none() is not None:
        raise AuthError(
            "un compte avec cet email existe déjà",
            f"duplicate email at registration: {request.email}"
        )
    
    hashed = hash_password(request.password)
    
    user = User(
        email = request.email,
        hashed_password = hashed,
        full_name = request.full_name,
        is_verified= True
    )
    
    session.add(user)
    await session.flush()
    await session.refresh(user)
    
    logging.info(f"User registered: id= {user.id}, email = {user.email}")
    
    return UserResponse(
        id = str(user.id),
        email= user.email,
        full_name= user.full_name,
        is_active = user.is_active,
        is_verified= user.is_verified,
        created_at= user.created_at
        
    )

