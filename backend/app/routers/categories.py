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

@router.get("/{category_id}", response_model=schemas.CategoryOut)
async def get_category(category_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Category).where(models.Category.id == category_id))
    category = res.scalar()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category

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

@router.delete("/{category_id}", response_model=schemas.CategoryOut)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session)):
    # Проверка существования категории
    res = await session.execute(select(models.Category).where(models.Category.id == category_id))
    category = res.scalar()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    # Проверка наличия связанных записей можно добавить позже
    
    # Удаляем категорию
    await session.delete(category)
    await session.commit()
    
    return category
