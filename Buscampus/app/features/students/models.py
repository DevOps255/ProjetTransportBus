import hashlib
import uuid
from datetime import datetime,timezone
from sqlmodel import Field, SQLModel
from typing import Optional


class Student(SQLModel, table=True):

    """cette entité représente un étudiant inscrit dans le système"""

    __tablename__ = "student"

    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    org_id: uuid.UUID = Field(foreign_key="organizations.id", index = True)

    student_number: str = Field(
        max_length=50,
        index=True,
        description="Numéro matricule de l'étudiant"
    )

    """
    phone_e164 stock le numéro au format international E.164 (+22890xxxxxx)
    
    sinon stocker de la manière classique pour un même numéro si un utilisateur
    
    change d'appareil peut créer des doublons et ça va casser la déduplication 
    de payements
    """

    phone_e164: str = Field(
        max_length=20,
        index=True,
        description="numéro Yas ou Moov format E.164"
    )

    is_active: bool = Field(default=True)
    create_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))




class DeviceFingerPrint(SQLModel, table=True):
    """l'empreinte d'un appareil lié à un étudiant """

    __tablename__ = "device_finger_print"

    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    student_id: uuid.UUID = Field(foreign_key="student.id", index = True)

    """
    device_hash est le SHA256 de l'identifiant brut de la pareil (Android ID, ou IDFV IOS)"""

    device_hash: str = Field(
        max_length=64,
        description="SHA256. 64 chars hex"

    )

    device_name: str = Field(
        max_length=100,
        default="",
        description="Nom comme TECNO KN3"
    )

    is_trusted: bool = Field(
        default=False,
        description="True après auth "
    )

    register_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    last_login_at: Optional[datetime] = Field(default=None)
