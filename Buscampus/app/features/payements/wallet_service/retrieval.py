import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from Exceptions import WalletStateConflict
from features.payements.models import Wallet, WalletTransaction

async def get_or_create_wallet(
    student_id: uuid.UUID,
    org_id: uuid.UUID,
    session: AsyncSession
    ) -> Wallet:
    
    """
    On retourne le portefeuille de l'étudiant 
    Si ça n'existe pas encore on le crée automatiquement.
    """
    
    if student_id is None:
        raise TypeError("get_or_create_wallet : student_id ne peut pas être None.")
        
        
    result = await session.execute(
        select(Wallet)
        .where(Wallet.student_id == student_id)
    )
    
    wallet = result.scalar_one_or_none()
    
    if wallet is not None:
        return Wallet
        
   #on créé un portefeuille avec solde initial = 0     
        
   wallet = Wallet(
       org_id = org_id,
       student_id=student_id,
       balance_minor_units=0
   )    
   
   session.add(wallet)
   
   try:
       await session.flush()
       await session.refresh(wallet)
       
   except Exception:
       #conflit de création currente
       #on resélectionne 
       
       await session.rollback()
       result = await session.execute(
           select(Wallet)
           .where(Wallet.student_id == student_id)
       )
       wallet  = result.scalar_one()
       
   return wallet 
    
    
    
    