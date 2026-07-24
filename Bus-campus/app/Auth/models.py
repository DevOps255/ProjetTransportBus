import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    email: str = Field(
        max_length=255,
        unique=True,
        index=True
    )
    
    hashed_password: str = Field(max_length=255)
    
    full_name: str = Field(max_length=255, default="")
    
    is_active: bool = Field(default=True)
    
    is_verfied: bool = Field(
        default=False,
        description="Email vérifié"
    )
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    
class Apikey(SQLModel, table=True):
    
    __tablename__ = "api-keys"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    user_id: uuid.UUID = Field(index=True, foreign_key="users.id")
    
    name: str = Field(
        max_length=100,
        description="Nom descriptif de la clé"
    )
    
    key_prefix: str= Field(
        max_length=20,
        index=True,
        description="les 8 premiers caractères de la clé (après le prefix sk_live_)"
    )
    
    hashed_key: str = Field(max_length=255)
    
    is_active: bool = Field(default=True)
    
    expire_at: datetime = Field(default=None)
    
    last_used_at: datetime | None = Field(default=None)
    
    created_at: datetime= Field(default_factory=lambda: datetime.now(timezone.utc))
    
    
class RefreshToken(SQLModel, table=True):
    
    __tablename__ = "refresh_tokens"
    
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    
    token_hash: str = Field(max_length=255, unique=True)
    
    is_revoked: bool = Field(default=False)
    
    expire_at: datetime = Field()
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    user_agent: str | None = Field(
        default=None,
        max_length=500,
        description="user-agent du client. Permet d'identifier l'appareil"
    )
    
    ip_client: str | None = Field(default=None, max_length=45)
    
    
    
    
    