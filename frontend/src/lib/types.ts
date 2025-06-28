// Общие типы для фронтенда семейного бюджета

export interface Account {
  id: string;
  name: string;
  balance: number;
}

export interface Category {
  id: string;
  name: string;
}

export interface Expense {
  id: string;
  spent_at: string;
  amount: number;
  description: string;
  category?: Category;
}

export interface Income {
  id: string;
  received_at: string;
  amount: number;
  description: string;
  category?: Category;
  account?: Account;
}

export interface SummaryItem {
  category: string;
  total: number;
}
