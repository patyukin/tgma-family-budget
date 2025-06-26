from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import models, schemas

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.get("/", response_model=List[schemas.AccountOut])
async def list_accounts(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Account))
    return res.scalars().all()

@router.post("/", response_model=schemas.AccountOut)
async def create_account(payload: schemas.AccountCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(models.Account).where(models.Account.name == payload.name))
    if exists.scalar():
        raise HTTPException(status_code=400, detail="Account already exists")
    account = models.Account(**payload.model_dump())
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account
