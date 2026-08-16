import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from typing import Optional


class BusLine(SQLModel, table=True):

    """
    cette entité concerne une route opérée par l'université de Kara

    le prix du ticket est stocké en centime de FCFA (Trop bizzare je sais)
    comme ça 150000 affichera 150.00f

    ça reste toujours un entier et non un flottant, les calculs d'argents sur
    des flottants accumulent des erreurs de représentation binaire qui peuvent
    produire 149.9999999... au lieu de 150f le prix du ticket
    """

    __tablename__ = "bus_lines"

    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)

    name:str = Field(
        max_length=255, index=True,
        description="nom de la ligne (ex: du Campus-Nord au Campus Sud"
    )

    code:str = Field(
        max_length=20,
        description="un code court pour la ligne qui est unique par org"
    )

    fare_amount: int = Field(
        ge=0,
        description="Le tarif en centime (15000= 150f)",
    )

    is_Active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) )


class BusStop(SQLModel, table=True):

    """
    un arrêt sur la ligne, par exemple un arrêt sur shell 2
    """

    __tablename__ = "bus_stops"

    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)

    line_id: uuid.UUID = Field(foreign_key="bus_lines.id", index=True)

    name: str = Field(max_length=255)

    """
    le stop_order définit la position de la ligne depuis dans la séquence
    de la ligne 
    par exemple le campus sud commence à la postion, ensuite shell  1 
    la position 2 et ainsi de suite
    ça peut être utile pour valider qu'un étudiant monte à un arret et
    y descent plus tard, et non l'inverse
    """

    stop_order : int = Field(
        ge=1,
        description="position dans la séquence de la ligne. On commence par 1"
    )

    latitude: float = Field(
        ge=90.0,
        le=90.0,

    )

    longitude: float = Field(
        ge=180.0,
        le=180.0,
    )

    is_active: bool = Field(default=True)
