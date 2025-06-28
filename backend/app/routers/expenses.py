from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
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

@router.get("/{expense_id}", response_model=schemas.ExpenseOut)
async def get_expense(expense_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Expense).options(selectinload(models.Expense.category)).where(models.Expense.id == expense_id))
    expense = res.scalar()
    if not expense:
        raise HTTPException(status_code=404, detail="Расход не найден")
    return expense

@router.delete("/{expense_id}", response_model=schemas.ExpenseOut)
async def delete_expense(expense_id: int, session: AsyncSession = Depends(get_session)):
    # Загружаем расход вместе с категорией
    res = await session.execute(
        select(models.Expense).options(
            selectinload(models.Expense.category)
        ).where(models.Expense.id == expense_id)
    )
    expense = res.scalar()
    if not expense:
        raise HTTPException(status_code=404, detail="Расход не найден")
    
    # Запоминаем данные для возврата до удаления объекта
    expense_data = schemas.ExpenseOut(
        id=expense.id,
        amount=expense.amount,
        description=expense.description,
        category_id=expense.category_id,
        account_id=expense.account_id,
        spent_at=expense.spent_at,
        category=schemas.CategoryOut(
            id=expense.category.id,
            name=expense.category.name
            # Убрали поле type, которого нет в модели Category
        ) if expense.category else None
    )
    
    # Восстанавливаем баланс счета при удалении расхода
    res = await session.execute(select(models.Account).where(models.Account.id == expense.account_id))
    account = res.scalar()
    if account:
        account.balance += expense.amount  # Возвращаем потраченную сумму обратно на счет
        session.add(account)
    
    await session.delete(expense)
    await session.commit()
    
    return expense_data

@router.get("/summary", response_model=List[schemas.ExpenseSummary])
async def summary_by_category(session: AsyncSession = Depends(get_session)):
    res = await session.execute(
        select(models.Category.name, func.sum(models.Expense.amount))
        .join(models.Expense, models.Expense.category_id == models.Category.id)
        .group_by(models.Category.name)
    )
    return [schemas.ExpenseSummary(category=row[0], total=row[1]) for row in res.all()]

@router.get("/summary/{month}", response_model=List[schemas.ExpenseSummary])
async def summary_by_category_month(month: str, session: AsyncSession = Depends(get_session)):
    # Формат month: YYYY-MM
    try:
        year, month_num = month.split('-')
        start_date = f"{month}-01"
        if month_num == "12":
            end_date = f"{int(year) + 1}-01-01"
        else:
            end_date = f"{year}-{int(month_num) + 1:02d}-01"
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат месяца. Используйте YYYY-MM")
    
    # Используем другой подход с функциями SQLAlchemy для даты
    sql = text("""
    SELECT c.name, COALESCE(SUM(e.amount), 0) as total
    FROM categories c
    LEFT JOIN expenses e ON e.category_id = c.id AND
                          e.spent_at >= to_date(:start_date, 'YYYY-MM-DD') AND
                          e.spent_at < to_date(:end_date, 'YYYY-MM-DD')
    GROUP BY c.name
    """)
    
    res = await session.execute(sql, {"start_date": start_date, "end_date": end_date})
    return [schemas.ExpenseSummary(category=row[0], total=row[1]) for row in res.all()]
