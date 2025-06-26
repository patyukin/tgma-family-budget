from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import models, schemas

router = APIRouter(prefix="/api/incomes", tags=["incomes"])

@router.post("/", response_model=schemas.IncomeOut)
async def create_income(payload: schemas.IncomeCreate, session: AsyncSession = Depends(get_session)):
    income = models.Income(**payload.model_dump())
    session.add(income)
    # update account balance
    account = await session.get(models.Account, payload.account_id)
    if account:
        account.balance += payload.amount
        await session.commit()
    # reload with category eagerly loaded
    res = await session.execute(
        select(models.Income).options(selectinload(models.Income.category)).where(models.Income.id == income.id)
    )
    return res.scalar_one()

@router.get("/", response_model=List[schemas.IncomeOut])
async def list_incomes(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Income).options(selectinload(models.Income.category)).order_by(models.Income.received_at.desc()))
    return res.scalars().all()
