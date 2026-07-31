import json
import logging

import httpx

from app.core.config import settings
from app.features.payements.schemas import SmsPaymentData, Operator


logger = logging.getLogger("payements.sms_parser")

class SmsParsingError(Exception):
    def __init__(self, public_message: str, internal_detail: str) -> None:
        self.public_message = public_message
        self.internal_detail = internal_detail
        super().__init_(internal_detail)

SYSTEM_PROMPT = """Tu es un extracteur de données financières spécialisé

dans les SMS de paiement mobile au Togo
 (Flooz de Moov Africa et Mixx de Yas (les nouveaux noms de T-money et Togocel)).

Ton unique rôle est d'extraire les informations de paiement depuis le texte brut d'un SMS 

et de les retourner dans la structure JSON demandée.
Formats reconnus :
Mixx(T-Money) : "Envoi de X FCFA au NUMERO(NOM), DATE. Frais: X FCFA. Nouveau solde Mixx: X FCFA. Ref: 18XXXXXXXXX."
Flooz : "Transfert de X FCFA vers NUMERO (NOM) effectue le DATE. Frais: X FCFA. Solde: X FCFA. Reference: FLXXXXXXXXXXXXXXXXXXX."


Règles absolues :
Si le SMS indique un échec, un refus, ou une annulation : succes=false
Les montants sont toujours des entiers en FCFA (150 FCFA = 150, pas 0.5)
Supprime les espaces et tirets dans les montants (1 000 = 1000)
Référence Flooz commence toujours par "FL"
Ne déduis jamais d'information qui n'est pas explicitement présente dans le SMS
En cas de doute sur la réussite du paiement, succes=false
numero_destinataire = le numéro qui A REÇU l'argent (pas l'expéditeur)
Je repète Ne jamais inventer une information absente du SMS


"""


async def parse_sms_payment(sms_text: str) -> SmsPaymentData:
    """
    on essait de parser le payement Mixx ou Flooz
    
    On essai gemini flash en premier. C'est rapide et 
    économique.
    
    Si le quota est dépassé c'est à dire renvoi une erreur HTTP 429
    
    on bascule vers Mistral.
    """
    
    if not sms_text or not sms_text.strip():
        raise SmsParsingError("SMS vide", "parsing sms_payment: sms_text vide")
        
        
    if len(sms_text) > 1000:
        
        raise SmsParsingError(
            "SMS invalide",
            f"sms_text trop long ({len(sms_text)} chars)"
        )
        
        
        
    try:
        return await _parse_with_gemini(sms_text)    
        
    except SmsParsingError as error:
        if "quota" in error.internal_detail.lower() or "429" in error.internal_detail:
            logger.warning("Le quota de Gemini est atteint. On bascule vers Mistral")
        else:
            logger.warning(f"Le parsing avec gemini a échoué {error.internal_detail}. on bascule vers Mistral")    
            
            
async def _parse_with_gemini(sms_text: str) -> SmsPaymentData:
    
    json_schema = 
    
    
    
    
    
    
    
    
    
    
    
    
    
        