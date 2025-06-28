<script lang="ts">
  import { onMount } from 'svelte';
  import { API_BASE_URL } from './lib/config';
  import type { Account, Expense, SummaryItem } from './lib/types';
  import ExpenseForm from './components/ExpenseForm.svelte';
  import IncomeForm from './components/IncomeForm.svelte';
  import ExpensesPage from './components/ExpensesPage.svelte';
  import IncomesPage from './components/IncomesPage.svelte';
  import AccountsPage from './components/AccountsPage.svelte';
  import CategoriesList from './components/CategoriesList.svelte';
  import ExpensesList from './components/ExpensesList.svelte';
  import Summary from './components/Summary.svelte';
  import AccountsList from './components/AccountsList.svelte';
  import ModalDialog from './components/ModalDialog.svelte';

  let expenses: Expense[] = [];
  let current: 'expenses' | 'incomes' | 'accounts' | 'categories' = 'expenses'; // expenses | incomes | accounts | categories
  let summary: SummaryItem[] = [];
  let accounts: Account[] = [];

  /**
   * Fetch без использования кеша, добавляет query-параметр ts и базовый URL API
   * @param {string} url - относительный путь API
   * @returns {Promise<Response>}
   */
  const fetchNoCache = (url: string): Promise<Response> => {
    const ts = Date.now();
    const fullUrl = `${API_BASE_URL}${url}`;
    const sep = fullUrl.includes('?') ? '&' : '?';
    return fetch(`${fullUrl}${sep}ts=${ts}`, { cache: 'no-store' });
  };

  const loadAccounts = async () => {
    const res = await fetchNoCache('/api/accounts/');
    accounts = await res.json();
  };
  const loadExpenses = async () => {
    const res = await fetchNoCache('/api/expenses/');
    expenses = await res.json();
  };
  const loadSummary = async () => {
    const res = await fetchNoCache('/api/expenses/summary');
    summary = await res.json();
  };

  const refresh = async () => {
    await loadExpenses();
    await loadSummary();
    await loadAccounts();
  };

  onMount(refresh);
</script>

<nav>
    <button on:click={() => current='expenses'} class:active={current==='expenses'}>Расходы</button>
    <button on:click={() => current='incomes'} class:active={current==='incomes'}>Доходы</button>
    <button on:click={() => current='accounts'} class:active={current==='accounts'}>Счета</button>
    <button on:click={() => current='categories'} class:active={current==='categories'}>Категории</button>
  </nav>

  <main>
  <h1>Семейный бюджет</h1>
  {#if current==='expenses'}
    <ExpensesPage {expenses} {summary} refreshGlobal={refresh} />
  {:else if current==='incomes'}
    <IncomesPage refreshGlobal={refresh} />
  {:else if current==='accounts'}
    <AccountsPage refreshGlobal={refresh} />
  {:else if current==='categories'}
    <CategoriesList />
  {/if}
</main>

<ModalDialog />

<style>
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
    font-family: Arial, sans-serif;
  }
  nav {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  nav button {
    padding: 0.5rem 1rem;
    border: none;
    background: #eee;
    cursor: pointer;
  }
  nav button.active {
    background: #2196f3;
    color: white;
  }
</style>
