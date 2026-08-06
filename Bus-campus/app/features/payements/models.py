import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import  Field, SQLModel



class GatewayPhone(SQLModel, table=True):

    __tablename__ = "gateway_phones"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    org_id: uuid.UUID = Field(foreign_key="organizations.id")

    phone_e164: str = Field(max_length=20)

    operateur: str = Field(max_length=20)

    priority: int = Field(default=1, ge=1)

    is_active: bool = Field(default=True)

    label: Optional[str] = Field(default=None, max_length=100)

    last_polled_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))


class Wallet(SQLModel, table=True):

    __tablename__ = "wallets"

    id:uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)

    student_id: uuid.UUID = Field(
        foreign_key="student.id",
        unique=True,
        description="Portefeuille unique par étudiant"
    )

    balance_minor_units: int = Field(
        default=0,
        ge=0,
        description="le solde"
    )

    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

    updated_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))



class WalletTransaction(SQLModel, table=True):

    __tablename__ = "wallet_transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    org_id: uuid.UUID = Field(foreign_key="organizations.id", index=True)

    wallet_id:uuid.UUID = Field(foreign_key="wallets.id", index=True)

    student_id: uuid.UUID = Field(foreign_key="student.id", index=True)

    type: str = Field(max_length=20)

    direction: str = Field(max_length=10)

    amount_minor_units: int = Field(gt=0)

    balance_after_minor_units: int = Field(ge=0)

    reference: Optional[str] = Field(default=None, max_length=100, unique=True)

    ticket_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tickets.id")

    operateur: Optional[str]  = Field(default=None, max_length=20)

    description: Optional[str] = Field(default=None, max_length=255)

    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))



class GatewaySmsQueue(SQLModel, table=True):

    __tablename__ = "gateway_sms_queue"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    gateway_id: uuid.UUID  = Field(foreign_key="gateway_phones.id", index=True)

    sms_text: str = Field()

    received_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

    processed_at: Optional[datetime] = Field(default=None)

    error_message: Optional[str] = Field(default=None, max_length=500)



