from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from .. import models, schemas

router = APIRouter(prefix="/api/budgets", tags=["budgets"])

@router.post("/", response_model=schemas.BudgetOut)
async def create_budget(payload: schemas.BudgetCreate, session: AsyncSession = Depends(get_session)):
    budget = models.Budget(**payload.model_dump())
    session.add(budget)
    await session.commit()
    await session.refresh(budget)
    return budget

@router.get("/", response_model=List[schemas.BudgetOut])
async def list_budgets(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Budget).order_by(models.Budget.month.desc()))
    return res.scalars().all()
