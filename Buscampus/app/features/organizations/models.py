import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, select, Field


class Organization(SQLModel, table=True):

    """
    Voici l'entité racine du système
    Toutes les entités métier sont liées à une organisation
    à travers leur org_id, c'est-à-dire, la colonne sur
    laquelle les politiques RLS (Row Level Security) filtrent
    """


    __tablename__ = "organizations"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    name: str = Field(
        max_length=255,
        unique=True,
        description="Nom du organisation (Université de Kara)"
    )
    """le slug, c'est à dire l'url 
    de l'UK étant donné qu'internet n'accepte pas des url du genre
    univ kara avec espace, pour l'UK c'est univkara.tg mais ça fait rien!
    """
    slug: str  = Field(
        max_length=255,
        unique=True,
         regex= r'^[a-z-0-9\-]+$',
        description="identifiant URL-safe de l'UK"
    )


    isActive: bool = Field(default=True)
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))