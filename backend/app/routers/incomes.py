from typing import List

from fastapi import APIRouter, Depends, HTTPException
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

@router.get("/{income_id}", response_model=schemas.IncomeOut)
async def get_income(income_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Income).options(selectinload(models.Income.category)).where(models.Income.id == income_id))
    income = res.scalar()
    if not income:
        raise HTTPException(status_code=404, detail="Доход не найден")
    return income

@router.delete("/{income_id}", response_model=schemas.IncomeOut)
async def delete_income(income_id: int, session: AsyncSession = Depends(get_session)):
    # Загружаем доход вместе с категорией
    res = await session.execute(
        select(models.Income).options(
            selectinload(models.Income.category)
        ).where(models.Income.id == income_id)
    )
    income = res.scalar()
    if not income:
        raise HTTPException(status_code=404, detail="Доход не найден")
    
    # Запоминаем данные для возврата до удаления объекта
    income_data = schemas.IncomeOut(
        id=income.id,
        amount=income.amount,
        description=income.description,
        category_id=income.category_id,
        account_id=income.account_id,
        received_at=income.received_at,
        category=schemas.CategoryOut(
            id=income.category.id,
            name=income.category.name
            # Убрали поле type, которого нет в модели Category
        ) if income.category else None
    )
    
    # Восстанавливаем баланс счета
    res = await session.execute(select(models.Account).where(models.Account.id == income.account_id))
    account = res.scalar()
    if account:
        account.balance -= income.amount
        session.add(account)
        
    # Удаляем доход
    await session.delete(income)
    await session.commit()
    
    return income_data

@router.get("/", response_model=List[schemas.IncomeOut])
async def list_incomes(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Income).options(selectinload(models.Income.category)).order_by(models.Income.received_at.desc()))
    return res.scalars().all()
