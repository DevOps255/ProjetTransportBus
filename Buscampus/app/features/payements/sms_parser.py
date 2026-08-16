import json
import logging

from mistralai.client import Mistral
import httpx
from Exceptions import SmsParsingError
from app.core.config import settings
from app.features.payements.schemas import SmsPaymentData
from LLM.gemini_key_manager.record_request_and_rate_limit import record_request, mark_rate_limited
from LLM.gemini_key_manager._load_and_select_key import select_available_key, GeminiKey

logger = logging.getLogger("payements.sms_parser")


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
        
        
        
    max_gemini_attempts = 3
    last_gemini_error: SmsParsingError | None = None
    
    for attempt in range(max_gemini_attempts):
        selected_key = await select_available_key()
        
        if selected_key is None:
            logger.warning(
                f"parse_sms_payment : aucune clé Gemini disponible "
                f"(tentative {attempt + 1}/{max_gemini_attempts}) On passe à  Mistral"
            )
            break
        try:
            result = await _parse_with_gemini(sms_text, selected_key)    
            await record_request(selected_key.label)
            return result
         
        except SmsParsingError as error:
            if "429" in error.internal_detail or "quota" in error.internal_detail.lower():
                await mark_rate_limited(selected_key.label)
                logger.warning(
                    f"parse_sms_payment : clé {selected_key.label} rate-limitée, "
                    f"prochain essai"
                )
                last_gemini_error = error
                continue
            else:
                """
                inutile de réesayer avec une nouvelle clé 
                c'est sûrement un problème non lié au quota (timeout, format invalide etc.)
                """
            last_gemini_error = error
            break  
              
    logger.warning(
        f"Gemini indisponible après {max_gemini_attempts} tentatives "
        f"On passe à Mistral"
    )    
    
    try:
        return await _parse_with_mistral(sms_text)
    except SmsParsingError as error:
        logger.error(f"Mistral aussi a échoué: {error.internal_detail}")    
        raise SmsParsingError(
            "Service d'analyse indisponible. Réessayez dans quelques instants.",
            f"Gemini et  Mistral ont échoué. "
            f"Dernière erreur Gemini : {last_gemini_error.internal_detail if last_gemini_error else 'N/A'}. "
            f"Erreur Mistral : {error.internal_detail}"
        )
        
        
        
async def _parse_with_gemini(sms_text: str, key: GeminiKey) -> SmsPaymentData:
    
    json_schema = SmsPaymentData.model_json_schema()
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": SYSTEM_PROMPT
                    }, {
                        "text": f"parse ce SMS de paiement :\n\n{sms_text}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json",
            "responseSchema": json_schema
        }
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-1.5-flash:generateContent?key={key.api_key}",
                    json=payload
            )
    except httpx.TimeoutException:
        raise SmsParsingError(
             "Délai d'analyse dépassé",
             f"Gemini timeout after 20s (clé={key.label})"
        ) 
    except httpx.RequestError as error:
        raise SmsParsingError(
            "Erreur de connexion au service d'analyse",
            f"Gemini request error (clé={key.label}) : {error}"
        ) 
        
           
    if response.status_code ==429:
        raise SmsParsingError(
            "quota atteint",
            f"Gemini 429 quota exceeded (clé={key.label}, projet={key.project_name})"
        )
        
    if response.status_code != 200:
        raise SmsParsingError(
            "Erreur d'analyse",
            f"Gemini HTTP {response.status_code} (clé={key.label}) : {response.text[:200]}"
        )    
        
    try:
        data = response.json()    
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        cleaned_response = raw_text.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.strip("`")
        if cleaned_response.startswith("json"):
            cleaned_response = cleaned_response[4:].strip()
        
        parsed_dict = json.loads(cleaned_response)
        return SmsPaymentData(**parsed_dict)
    except(KeyError, IndexError, json.JSONDecodeError) as error:
        raise SmsParsingError(
            "Données extraites Invalides ",
            f"Pydantic validation failed (clé={key.label}) : {error}",
            
        )
    
async def _parse_with_mistral(sms_text: str) -> SmsPaymentData:
    """
    Mistral est appelé dans le cas où toutes les clés 
    de Gemini sont indisponible simultanément 
    
    En temps normal, et franchement la probabilité est très faible 
    que cette fonction soit appelée
    c'est juste le dernier filet de securité
    """
    try:
        client = Mistral(api_key=settings.Mistral_key)
        
        response = await client.chat.complete_async(
            model=settings.Mistral_model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }, {
                    "role": "user",
                    "content": f"parse ce sms:\n\n:{sms_text} "
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0.0
        )
        raw = response.choices[0].message.content
        
        if not raw:
            raise SmsParsingError(
                "Réponse vide",
                "Mistral return empty content"
            )
        cleaned_response = raw.strip()
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.strip("`")
        if cleaned_response.startswith("json"):
            cleaned_response = cleaned_response[4:].strip()
            
        data = json.loads(cleaned_response)
        return SmsPaymentData(**data)
    
    except SmsParsingError:
        raise
        
    except json.JSONDecodeError as error:
        raise SmsParsingError(
            "Format de réponse inattendu.",
            f"Mistral JSON invalide : {error}",
        )
    except Exception as err:
        raise SmsParsingError(
             "Service indisponible.",
             f"Mistral error : {err}"
        )
    
    
    
    
    
    
        