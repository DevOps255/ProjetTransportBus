import logging
import uuid

from core.config import settings
from Exceptions import WalletOperationFailure
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlmodel import select
from features.payements.models import Wallet, WalletTransaction
from features.payements.wallet_service.retrieval import get_or_create_wallet

logger = logging.getLogger("payments.wallet")
async def credit_wallet(
    student_id: uuid.UUID,
    org_id: uuid.UUID,
    amount_minor_units: int,
    reference: str,
    operateur: str,
    session: AsyncSession
    ) -> Wallet:
   
    """
    crédite le portfeuille d'un étudiant après une
    recharge.
    """
    if amount_minor_units is None:
        raise TypeError("credit_wallet : amount_minor_units ne peut pas être None.")
    if amount_minor_units <= 0:
        raise WalletOperationFailure(
            "Montant de recharge invalide.",
            f"credit_wallet : amount_minor_units={amount_minor_units} invalide."
        )
            
    if  amount_minor_units < settings.minimum_recharge_minor_units:
        raise WalletOperationFailure(
            f"Recharge minimum : {settings.minimum_recharge} FCFA."
            f"Montant reçu : {amount_minor_units // 100} FCFA.",
            f"credit_wallet : montant {amount_minor_units} < minimum {settings.minimum_recharge_minor_units}"
        )
        
    if not reference or not reference.strip():
        raise WalletOperationFailure(
            "Référence de paiement manquante.",            
            "credit_wallet : reference vide."
        )
        
    result = await session.execute(
        text("""
        SELECT id, balance_minor_units
        FROM wallets
        WHERE student_id = :student_id
        FOR UPDATE
        """),
        {
            "student_id": str(student_id)
        }
    )
    row = result.fetchone()
    
    if row is None:
        wallet = await get_or_create_wallet(student_id, org_id, session)
        wallet_id = wallet.id
        current_balance = 0
        
    else:
        wallet_id = row[0]     
        current_balance = row[1]
        
    new_balance = current_balance + amount_minor_units
    
    # Mise à jour du sole 
    
    await session.execute(
        text("""
        UPDATE wallets
        SET balance_minor_units = :new_balance,
            updated_at = NOW()
        WHERE id = :wallet_id    
        """),{
            "new_balance": new_balance,
            "wallet_id": str(wallet_id)
        }
    )
    
    # Enregistrement de la transaction 
    
    tx = WalletTransaction(
         org_id=org_id,
         wallet_id=wallet_id,
         student_id=student_id,
         type="recharge",
         direction="credit",
         amount_minor_units=amount_minor_units,
         balance_after_minor_units=new_balance,
         reference=reference.strip().upper(),
         operateur=operateur,
         description=f"Recharge {operateur.upper()}, {amount_minor_units // 100} FCFA"
    )
    
    session.add(tx)
    await session.flush()
    
    logger.info(
        f"Wallet credited : student={student_id}, "
        f"amount={amount_minor_units // 100} FCFA, "
        f"new_balance={new_balance // 100} FCFA, "
        f"ref={reference[:8]}..."
    )
    updated = await session.execute(
        select(Wallet)
        .where(Wallet.id == wallet_id)
    )
    return updated.scalar_one()
    
    
    
    
    