from typing import Optional, List, Literal
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
    account_id: int
    description: Optional[str] = None

class ExpenseOut(BaseModel):
    id: int
    amount: condecimal(max_digits=14, decimal_places=2)
    category: Optional[CategoryOut] = None
    account_id: int
    description: Optional[str] = None
    spent_at: datetime

    class Config:
        from_attributes = True

class IncomeCreate(BaseModel):
    amount: condecimal(max_digits=14, decimal_places=2)
    category_id: Optional[int] = None
    account_id: int
    description: Optional[str] = None

class IncomeOut(BaseModel):
    id: int
    amount: condecimal(max_digits=14, decimal_places=2)
    category: Optional[CategoryOut] = None
    account_id: int
    description: Optional[str] = None
    received_at: datetime

    class Config:
        from_attributes = True

class AccountCreate(BaseModel):
    name: str
    balance: Optional[condecimal(max_digits=14, decimal_places=2)] = 0

class AccountOut(BaseModel):
    id: int
    name: str
    balance: condecimal(max_digits=14, decimal_places=2)

    class Config:
        from_attributes = True

class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: condecimal(max_digits=14, decimal_places=2)
    description: Optional[str] = None

class TransferOut(BaseModel):
    id: int
    from_account_id: int
    to_account_id: int
    amount: condecimal(max_digits=14, decimal_places=2)
    description: Optional[str] = None
    transferred_at: datetime

    class Config:
        from_attributes = True

class BudgetCreate(BaseModel):
    category_id: int
    month: datetime
    planned: condecimal(max_digits=14, decimal_places=2)

class BudgetOut(BaseModel):
    id: int
    category: Optional[CategoryOut]
    month: datetime
    planned: condecimal(max_digits=14, decimal_places=2)

    class Config:
        from_attributes = True

class ExpenseSummary(BaseModel):
    category: Optional[str]
    total: condecimal(max_digits=14, decimal_places=2)
