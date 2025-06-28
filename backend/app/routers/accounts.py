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

@router.get("/{account_id}", response_model=schemas.AccountOut)
async def get_account(account_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Account).where(models.Account.id == account_id))
    account = res.scalar()
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")
    return account

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

@router.delete("/{account_id}", response_model=schemas.AccountOut)
async def delete_account(account_id: int, session: AsyncSession = Depends(get_session)):
    # Сначала проверяем, существует ли счёт
    res = await session.execute(select(models.Account).where(models.Account.id == account_id))
    account = res.scalar()
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")
    
    # Проверка наличия связанных записей (можно добавить позже)
    
    # Удаляем счёт
    await session.delete(account)
    await session.commit()
    
    return account
