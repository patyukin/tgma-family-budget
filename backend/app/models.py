from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, DateTime, Date, func
from sqlalchemy.orm import relationship

from .database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)

    expenses = relationship("Expense", back_populates="category")
    incomes = relationship("Income", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    description = Column(Text)
    spent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    category = relationship("Category", back_populates="expenses")
    account = relationship("Account", back_populates="expenses")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    balance = Column(Numeric(14, 2), nullable=False, default=0)

    incomes = relationship("Income", back_populates="account")
    expenses = relationship("Expense", back_populates="account")
    transfers_out = relationship("Transfer", back_populates="from_account", foreign_keys="Transfer.from_account_id")
    transfers_in = relationship("Transfer", back_populates="to_account", foreign_keys="Transfer.to_account_id")

class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    description = Column(Text)
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    category = relationship("Category", back_populates="incomes")
    account = relationship("Account", back_populates="incomes")

class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey("accounts.id"))
    to_account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Numeric(14, 2), nullable=False)
    description = Column(Text)
    transferred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    from_account = relationship("Account", foreign_keys=[from_account_id], back_populates="transfers_out")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="transfers_in")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    month = Column(Date, nullable=False)
    planned = Column(Numeric(14, 2), nullable=False)

    category = relationship("Category", back_populates="budgets")
