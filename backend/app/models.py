from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)

    expenses = relationship("Expense", back_populates="category")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    description = Column(Text)
    spent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    category = relationship("Category", back_populates="expenses")
