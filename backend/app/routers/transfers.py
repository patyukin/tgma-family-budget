from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import models, schemas

router = APIRouter(prefix="/api/transfers", tags=["transfers"])

@router.post("/", response_model=schemas.TransferOut)
async def create_transfer(payload: schemas.TransferCreate, session: AsyncSession = Depends(get_session)):
    if payload.from_account_id == payload.to_account_id:
        raise HTTPException(status_code=400, detail="Accounts must be different")

    from_acc = await session.get(models.Account, payload.from_account_id)
    to_acc = await session.get(models.Account, payload.to_account_id)
    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if from_acc.balance < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    transfer = models.Transfer(**payload.model_dump())
    from_acc.balance -= payload.amount
    to_acc.balance += payload.amount

    session.add(transfer)
    await session.commit()
    await session.refresh(transfer)
    return transfer

@router.get("/", response_model=List[schemas.TransferOut])
async def list_transfers(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Transfer).order_by(models.Transfer.transferred_at.desc()))
    return res.scalars().all()
