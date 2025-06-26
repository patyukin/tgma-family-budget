from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_session
from .. import models, schemas

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("/", response_model=List[schemas.CategoryOut])
async def list_categories(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(models.Category))
    return result.scalars().all()

@router.post("/", response_model=schemas.CategoryOut)
async def create_category(payload: schemas.CategoryCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(models.Category).where(models.Category.name == payload.name))
    if exists.scalar():
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = models.Category(**payload.model_dump())
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat
