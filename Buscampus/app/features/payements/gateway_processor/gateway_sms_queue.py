import logging 
import json
import uuid
from datetime import datetime, timezone

from features.payements.gateway_processor.process_sms_queue
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from sqlalchemy import text
from features.students.models import Student
from features.payements.models import GatewaySmsQueue, GatewayPhone

logger = logging.getLogger("payments.gateway_processor")

async def process_gateway_sms_queue() -> None:
    
    """
    Tâche APScheduler exécutée toutes les 10 secondes.    
    Lit les SMS non traités dans gateway_sms_queue,
    les parse avec Gemini/Mistral, et crédite les portefeuilles.
    Cette fonction crée sa propre session async 
     
    elle s'exécute  dans le contexte APScheduler, pas dans celui d'une requête FastAPI
    """
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
            SELECT q.id, q.sms_text, q.gateway_id,
                g.phone_e164 as gateway_phone,
                g.operateur
            FROM gateway_sms_queue q
            JOIN gateway_phones g ON q.gateway_id = g.id
            WHERE q.processed = FALSE
            ORDER BY q.received_at ASC
            LIMIT 50
            """)
        )
        pending = result.fetchall()
        
        if not pending:
            return 
        
        logger.info(f"Gateway processor : {len(pending)} SMS en attente")    
        
        gateways = await session.execute(
            select(GatewayPhone)
            .where(GatewayPhone.is_active == True)
        )
        
        bus_campus_phones= [g.phone_e164 for g in gateways.scalars().all()]
        
        for row in pending:
            sms_queue_id = row[0]
            sms_text = row[1]
            gateway_phone= row[3]
            
            success = await _process_single_sms()
            
            
            
            
            