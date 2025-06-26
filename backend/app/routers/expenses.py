from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List

from ..database import get_session
from .. import models, schemas

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

@router.post("/", response_model=schemas.ExpenseOut)
async def create_expense(payload: schemas.ExpenseCreate, session: AsyncSession = Depends(get_session)):
    expense = models.Expense(**payload.model_dump())
    session.add(expense)

    # update account balance
    account = await session.get(models.Account, payload.account_id)
    if account:
        if account.balance < payload.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds on account")
        account.balance -= payload.amount

        await session.commit()
    # reload with category eagerly loaded to avoid greenlet issues
    res = await session.execute(
        select(models.Expense).options(selectinload(models.Expense.category)).where(models.Expense.id == expense.id)
    )
    return res.scalar_one()

@router.get("/", response_model=List[schemas.ExpenseOut])
async def list_expenses(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Expense).options(selectinload(models.Expense.category)).order_by(models.Expense.spent_at.desc()))
    return res.scalars().all()

@router.get("/summary", response_model=List[schemas.ExpenseSummary])
async def summary_by_category(session: AsyncSession = Depends(get_session)):
    res = await session.execute(
        select(models.Category.name, func.sum(models.Expense.amount))
        .join(models.Expense, models.Expense.category_id == models.Category.id)
        .group_by(models.Category.name)
    )
    return [schemas.ExpenseSummary(category=row[0], total=row[1]) for row in res.all()]
