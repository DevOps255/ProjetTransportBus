from enum import Enum
from pydantic import BaseModel, Field

class Operator(str, Enum):
    
    """
    Les deux opérateurs mobiles au Togo
    
    """
    
    Flooz = "flooz"
    Mixx = 'Mixx'

class SmsPaymentData(BaseModel):
    
    """
    Structure de donnée extraite d'un sms de confirmation
    de payment avec les LLM
    
    ce modèle joue deux rôles 
    
    D'abord il génère le schéma JSON qui sera envoyé aux 
    LLMs 
    
    et il valide la sortie des LLMs
    """
    
    succes: bool = Field(
        description=(
            "True si le SMS confirme un payement réussi"
            "False si le SMS indique un échec, un refus ou une"
            "transaction annullée. Dès qu'on a le moindre toute on mets False"
        )
        
    )
    montant: int | None = Field(default=None, ge=1, le=1_000_000)
    
    reference: str | None = Field(
        default=None,
        min_length=5,
        max_length=100
    )
    
    provider: Operator | None = Field(default=None)
    
    sender_number: str | None = Field(default=None)
    
    failed_reason: str | None = Field(default=None)
    
    