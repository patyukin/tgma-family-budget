from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, condecimal


class CategoryCreate(BaseModel):
    name: str

class CategoryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    amount: condecimal(max_digits=14, decimal_places=2)
    category_id: Optional[int] = None
    description: Optional[str] = None

class ExpenseOut(BaseModel):
    id: int
    amount: condecimal(max_digits=14, decimal_places=2)
    category: Optional[CategoryOut] = None
    description: Optional[str] = None
    spent_at: datetime

    class Config:
        from_attributes = True

class ExpenseSummary(BaseModel):
    category: Optional[str]
    total: condecimal(max_digits=14, decimal_places=2)
