import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from typing import Optional

class Bus(SQLModel, table=True):

    """Un vrai véhicule (bus) qui appartient à l'UK"""

    __tablename__ = "buses"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    """plate_number est correspond à la plaque d'immatriculation d'un bus de l'UK
    c'est unique pour chaque organisation; mais en vrai deux org peuvent avoir la même
    plaque même si c'est très peu possible
    """

    plate_number: int = Field(max_length=20)

    capacity:int = Field(ge= 1, le=200, description="Nombre maximal de passagers. Entre 1 et 200")

    status: str=Field(
        default="active",
        max_length=20,
        description="Active ou Maintenance ou en retrait",

    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

