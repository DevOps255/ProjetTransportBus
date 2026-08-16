import json
import uuid

from features.payements.sms_parser import parse_sms_payment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from features.payements.sms_parser import parse_sms_payment
from Exceptions import SmsParsingError
from features.payements.idempotency import claim_reference_level2
from features.payements.gateway_processor.gateway_sms_queue import logger
from core.config import settings

async def _process_single_sms(
    sms_queue_id: uuid.UUID,
    sms_text: str,
    bus_campus_phones: list[str],
    session: AsyncSession
    ) -> bool: 
    
    """
    Traite un SMS de recharge depuis la file passerelle.
    alors le flux, il est simple
    
    on prend le SMS brut, on le parse à Gemini ou Mistral 
    On vérifie:
    si le paiement est confirmé
    si la référence est présente
    si la référence a déjà été traitée
    si le Montant est suffisant
    si Destinataire est celui prévu 
    Si l'étudiant est identifié 
    
    Retourne True si le portefeuille a été crédité.
    Retourne False si erreur (logged).
    """
    try:
        #parsing LLM
        
        sms_data = await parse_sms_payment(sms_text)
        
    except SmsParsingError as err:
        if "indisponible" in err.public_message:
            logger.warning(f"Agent IA indisponible. SMS reporté au prochain cycle")
            return False
        logger.warning(f"SMS {sms_queue_id} non parseable : {err.internal_detail}")
        
        
    if not sms_data.succes:
        
        logger.info(f"SMS {sms_queue_id} : paiement non confirmé ({sms_data.failed_reason})")
        
        
    if sms_data.reference is None or sms_data.montant is None:
        
        logger.warning(f"SMS {sms_queue_id} : données manquantes après parsing")
        return False
   
    # indempotence de niveau 2, on vérifie si la référence est deja traité.
    
    claimed = await claim_reference_level2(sms_data.reference)
    
    if not claimed:
        logger.info(f"SMS {sms_queue_id} : référence {sms_data.reference[:8]}... déjà traitée")
        return True
        
    # Vérificiation du montant 
    
    amount_minor_units = sms_data.montant * 1000
    
    if amount_minor_units < settings.minimum_recharge_minor_units:
        logger.warning(
            f"SMS {sms_queue_id} : montant {sms_data.montant} FCFA"
            f"inférieur minimum {settings.minimum_recharge_minor_units // 100} FCFA"
            
        )
        return False
        
    #Verfication du destinataire
    
    if sms_data.    
    
    
    
    
    
    