import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Topic(SQLModel, table=True):
    __tablename__ = "topic"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4 )

    nom: str = Field(max_length=255, min_length=1, unique=True)

    created_at : datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
