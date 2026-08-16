import uuid

from Exceptions import WalletOperationFailure
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from payements.models import Wallet, WalletTransaction
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
   
   new_balance = current_balance - amount_minor_units
   await session.execute(
       text("""
       UPDATE wallets
       SET balance_minor_units = :new_balance,
       	updated_at = NOW()
       WHERE id = :wallet_id    
       """), {
           "new_balance": new_balance,
           "wallet_id": str(wallet_id)
       }
   )
   
   tx = WalletTransaction(
       org_id=org_id,        
       wallet_id=wallet_id,        
       student_id=student_id,        
       type="purchase",        
       direction="debit",        
       amount_minor_units=amount_minor_units,        
       balance_after_minor_units=new_balance,        
       ticket_id=ticket_id,
       description=f"Achat ticket: {amount_minor_units // 100} FCFA",
   )
   
   session.add(tx)
   await session.flush()
   
   logger.info(
       f"Wallet debited : student={student_id}, "        
       f"amount={amount_minor_units // 100} FCFA, "        
       f"new_balance={new_balance // 100} FCFA, "        
       f"ticket={ticket_id}"
   )
   
   updated = await session.execute(
       select(Wallet)
       .where(Wallet.id == wallet_id)
   )
   return updated.scalar_one()
    
    