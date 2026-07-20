import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Trip(SQLModel, table=True):

   """cette entité est une instance unique de bus sur une ligne à un moment donné
   bon! disons que c'est l'entité qui est au centre du système

   un ticket doit toujours référencer un trip  et non une BusLine directement.

   comme cela on peut gérer les trajets qui ne sont pas prévus (comme des bus
   supplémentaires et les annulations

   """

   __tablename__ = "trips"

   id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

   org_id: uuid.UUID = Field(foreign_key="organizations.id")

   line_id: uuid.UUID = Field(foreign_key="bus_lines.id")

   bus_id: uuid.UUID = Field(foreign_key="buses.id", index=True)

   scheduled_arrival: datetime = Field(
      index=True,
      description="heure d'arrivée du bus planifié"
   )

   scheduled_departure: datetime = Field(
      description="heure de départ planifiée"
   )

   actual_departure: Optional[datetime] = Field(
      default=None,
      description="heure de  départ réelle. Null avant le départ"
   )

   status: str = Field(
      default="scheduled",
      max_length=20,
      description="scheduled, boarding, in_progress, cancelled, completed"
   )


   created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



