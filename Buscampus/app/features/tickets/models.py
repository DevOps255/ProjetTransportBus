import uuid

from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from typing import Optional


class Ticket(SQLModel, table=True):

    """le ticket est en quelque sorte la preuve qu'un étudiant a le droit de monter dans
    un bus"""

    __tablename__ = "tickets"

    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)

    student_id: uuid.UUID = Field(foreign_key="student.id", index=True)

    line_id : uuid.UUID = Field(foreign_key="bus_lines.id", index=True)

    boarding_stop_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bus_stops.id")

    alighting_stop_id: Optional[uuid.UUID] = Field(default=None, foreign_key="bus_stops.id")

    device_finger_print:uuid.UUID = Field(foreign_key="device_finger_print.id",
                                index=True, description="l'appareil depuis lequel le ticket a été acheté")


    status: str=Field(
        default='pending_payement',
        max_length=20,
        index=True,
    )

    totp_secret: str= Field(
        max_length=64,
        unique=True,
        description="Secret TOTP base64"
    )

    purchase_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date d'achat du ticket"
    )

    used_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

class Payment(SQLModel, table=True):
    
    __tablename__="payments"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)
    
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", index=True)
    
    students_id: uuid.UUID = Field(foreign_key="student.id", index=True)
    
    payment_reference: str = Field(max_length=100,unique=True, index=True)
    
    amount: int = Field(ge=0)
    
    phone_e164:str = Field(max_length=20)
    
    status: str = Field (
        default="pending", 
        max_length=20,
        description="pending - confirmed - refunded - failed"
        )
    
    confirmed_at: datetime | None = Field(default=None)
    
    refund_of_payment_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="payments.id",
        description="si ce paiement est un remboursement, on référence le paiement original"
    )
    
    created_at: datetime | None = Field(default_factory=lambda:datetime.now(timezone.utc))
    
    




