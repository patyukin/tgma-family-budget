import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import App from './App.svelte';

// Мокаем fetch перед тестами
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('App', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    
    // Настраиваем моки для fetch
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/api/expenses')) {
        return Promise.resolve({
          json: () => Promise.resolve([
            { id: '1', description: 'Продукты', amount: 1000, spent_at: '2025-06-28' }
          ])
        });
      }
      if (url.includes('/api/expenses/summary')) {
        return Promise.resolve({
          json: () => Promise.resolve([
            { category: 'Продукты', total: 1000 }
          ])
        });
      }
      if (url.includes('/api/accounts')) {
        return Promise.resolve({
          json: () => Promise.resolve([
            { id: '1', name: 'Наличные', balance: 5000 }
          ])
        });
      }
      return Promise.resolve({ json: () => Promise.resolve([]) });
    });
  });

  it('отображает заголовок приложения', async () => {
    render(App);
    expect(screen.getByText('Семейный бюджет')).toBeInTheDocument();
  });

  it('загружает и отображает вкладку расходов по умолчанию', async () => {
    render(App);
    
    // Проверяем, что страница расходов активна по умолчанию
    const expensesButton = screen.getByText('Расходы');
    expect(expensesButton).toHaveClass('active');
    
    // Проверяем, что запрос к API выполнен
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/expenses\/.+/), 
      expect.anything()
    );
  });

  it('переключается между вкладками', async () => {
    render(App);
    
    // Переключаемся на вкладку доходов
    const incomesButton = screen.getByText('Доходы');
    await fireEvent.click(incomesButton);
    
    // Проверяем, что кнопка активная
    expect(incomesButton).toHaveClass('active');
    
    // Переключаемся на вкладку счетов
    const accountsButton = screen.getByText('Счета');
    await fireEvent.click(accountsButton);
    
    // Проверяем, что кнопка активная
    expect(accountsButton).toHaveClass('active');
    
    // Переключаемся на вкладку категорий
    const categoriesButton = screen.getByText('Категории');
    await fireEvent.click(categoriesButton);
    
    // Проверяем, что кнопка активная
    expect(categoriesButton).toHaveClass('active');
  });
});
