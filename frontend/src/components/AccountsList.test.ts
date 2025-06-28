import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import AccountsList from './AccountsList.svelte';
import type { Account } from '../lib/types';

describe('AccountsList', () => {
  const mockAccounts: Account[] = [
    { id: '1', name: 'Наличные', balance: 1000 },
    { id: '2', name: 'Карта', balance: 5000 },
  ];

  it('отображает список счетов', () => {
    const onDeposit = vi.fn();
    render(AccountsList, { props: { accounts: mockAccounts, onDeposit } });
    
    // Проверяем, что имена счетов отображаются
    expect(screen.getByText('Наличные')).toBeInTheDocument();
    expect(screen.getByText('Карта')).toBeInTheDocument();
    
    // Проверяем, что отображается баланс
    expect(screen.getByText('1000')).toBeInTheDocument();
    expect(screen.getByText('5000')).toBeInTheDocument();
  });

  it('вызывает onDeposit при нажатии на кнопку пополнения', async () => {
    const onDeposit = vi.fn();
    render(AccountsList, { props: { accounts: mockAccounts, onDeposit } });
    
    // Находим все кнопки пополнения
    const depositButtons = screen.getAllByText('+ Пополнить');
    // Кликаем по первой кнопке
    await fireEvent.click(depositButtons[0]);
    
    // Проверяем, что функция onDeposit была вызвана с правильным аргументом
    expect(onDeposit).toHaveBeenCalledWith(mockAccounts[0]);
  });

  it('отображает пустую таблицу, когда нет счетов', () => {
    const onDeposit = vi.fn();
    render(AccountsList, { props: { accounts: [], onDeposit } });
    
    // Проверяем, что заголовки таблицы отображаются
    expect(screen.getByText('Счёт')).toBeInTheDocument();
    expect(screen.getByText('Баланс')).toBeInTheDocument();
    
    // Проверяем, что нет строк с данными
    expect(screen.queryByRole('cell')).not.toBeInTheDocument();
  });
});
