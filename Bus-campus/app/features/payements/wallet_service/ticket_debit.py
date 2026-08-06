import uuid

from Exceptions import WalletOperationFailure
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from payements.models import Wallet
from core.config import settings

async def debit_wallet_for_ticket(
    student_id: uuid.UUID,
    org_id: uuid.UUID,
    ticket_id: uuid.UUID,
    amount_minor_units: int,
    session: AsyncSession
    ) -> Wallet:
    
    """
    Débite le portefeuille pour l'achat d'un ticket 
    """
    
    if ticket_id  is None:
        raise TypeError(
            "debit_wallet_for_ticket : ticket_id ne peut pas être None."
        )
        
    if amount_minor_units  <= 0:
        raise WalletOperationFailure(
              "Montant invalide.",
              f"debit_wallet_for_ticket : amount={amount_minor_units} invalide."
        )
    
    result = await session.execute(
        text("""
        SELECT id, balance_minor_units
        FROM wallets
        WHERE student_id = :student_id
        FOR UPDATE
        """), {
            "student_id": str(student_id)
        }
    )    
    row = result.fetchone()
    
    if row is None:
        raise WalletOperationFailure(
            "Portefeuille introuvable. Rechargez votre compte avant d'acheter un ticket.",
            f"debit_wallet_for_ticket : wallet absent pour student={student_id}"
        )
        
    wallet_id = row[0]    
    current_balance = row[1]
        
   if current_balance < amount_minor_units:
       raise WalletOperationFailure(
            f"Solde insuffisant. "            
            f"Solde actuel : {current_balance // 100} FCFA. "
            f"Montant requis : {amount_minor_units // 100} FCFA.",            
            f"debit_wallet_for_ticket : balance={current_balance} < amount={amount_minor_units}"
       )
   
       
        
    
    
    
    
    
    
    
    
    
    