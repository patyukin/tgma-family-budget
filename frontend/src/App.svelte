<script lang="ts">
  import { onMount } from 'svelte';
  import { API_BASE_URL } from './lib/config';
  import type { Account, Expense, SummaryItem } from './lib/types';
  import { debug, info, warn, error, logApiRequest, logApiResponse } from './lib/logger';
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
  let isLoading = {
    expenses: false,
    summary: false,
    accounts: false
  };
  let loadErrors: {
    expenses: Error | null,
    summary: Error | null,
    accounts: Error | null
  } = {
    expenses: null,
    summary: null,
    accounts: null
  };
  
  // Информация о приложении
  info('Приложение инициализировано', { 
    apiBaseUrl: API_BASE_URL, 
    environment: import.meta.env.PROD ? 'production' : 'development',
    buildTime: new Date().toISOString()
  });

  /**
   * Fetch без использования кеша, добавляет query-параметр ts и базовый URL API
   * @param {string} url - относительный путь API
   * @returns {Promise<Response>}
   */
  const fetchNoCache = (url: string): Promise<Response> => {
    const ts = Date.now();
    const fullUrl = `${API_BASE_URL}${url}`;
    const sep = fullUrl.includes('?') ? '&' : '?';
    const finalUrl = `${fullUrl}${sep}ts=${ts}`;
    
    logApiRequest('GET', finalUrl, { cache: 'no-store' });
    debug(`API запрос: ${finalUrl}`, { timestamp: ts, baseUrl: API_BASE_URL });
    
    return fetch(finalUrl, { cache: 'no-store' })
      .then(response => {
        if (!response.ok) {
          error(`API ошибка: ${response.status} ${response.statusText} для ${url}`);
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        return response;
      })
      .catch(err => {
        error(`Сетевая ошибка при запросе ${url}:`, err);
        throw err;
      });
  };

  const loadAccounts = async () => {
    const endpoint = '/api/accounts/';
    isLoading.accounts = true;
    loadErrors.accounts = null;
    
    try {
      debug(`Загрузка счетов начата`);
      const res = await fetchNoCache(endpoint);
      const data = await logApiResponse(res, endpoint);
      accounts = data;
      info(`Загружено ${accounts.length} счетов`);
    } catch (err) {
      loadErrors.accounts = err instanceof Error ? err : new Error(String(err));
      error('Ошибка при загрузке счетов:', err);
    } finally {
      isLoading.accounts = false;
    }
  };
  
  const loadExpenses = async () => {
    const endpoint = '/api/expenses/';
    isLoading.expenses = true;
    loadErrors.expenses = null;
    
    try {
      debug(`Загрузка расходов начата`);
      const res = await fetchNoCache(endpoint);
      const data = await logApiResponse(res, endpoint);
      expenses = data;
      info(`Загружено ${expenses.length} расходов`);
    } catch (err) {
      loadErrors.expenses = err instanceof Error ? err : new Error(String(err));
      error('Ошибка при загрузке расходов:', err);
    } finally {
      isLoading.expenses = false;
    }
  };
  
  const loadSummary = async () => {
    const endpoint = '/api/expenses/summary/';
    isLoading.summary = true;
    loadErrors.summary = null;
    
    try {
      debug(`Загрузка сводки начата`);
      const res = await fetchNoCache(endpoint);
      const data = await logApiResponse(res, endpoint);
      summary = data;
      info(`Загружена сводка: ${summary.length} записей`);
    } catch (err) {
      loadErrors.summary = err instanceof Error ? err : new Error(String(err));
      error('Ошибка при загрузке сводки:', err);
    } finally {
      isLoading.summary = false;
    }
  };

  const refresh = async () => {
    info(`Обновление данных запущено`);
    const startTime = Date.now();
    
    try {
      await loadExpenses();
      await loadSummary();
      await loadAccounts();
      
      const endTime = Date.now();
      info(`Обновление данных завершено за ${endTime - startTime}ms`);
    } catch (err) {
      error('Ошибка при обновлении данных:', err);
    }
  };

  onMount(() => {
    debug('Компонент смонтирован, запуск обновления данных');
    refresh();
  });
</script>

<nav>
    <button on:click={() => current='expenses'} class:active={current==='expenses'}>Расходы</button>
    <button on:click={() => current='incomes'} class:active={current==='incomes'}>Доходы</button>
    <button on:click={() => current='accounts'} class:active={current==='accounts'}>Счета</button>
    <button on:click={() => current='categories'} class:active={current==='categories'}>Категории</button>
  </nav>

  <main>
  <h1>Семейный бюджет</h1>
  
  <!-- Отладочная информация -->
  <div class="debug-panel">
    <details>
      <summary>Отладочная информация</summary>
      <div class="debug-content">
        <div>
          <h4>API Base URL: {API_BASE_URL || '(относительный)'}</h4>
          <h4>Режим: {import.meta.env.PROD ? 'Production' : 'Development'}</h4>
        </div>
        
        <div>
          <h4>Статус загрузки:</h4>
          <ul>
            <li>Расходы: {isLoading.expenses ? '⏱️ загрузка...' : '✅ загружено'}</li>
            <li>Сводка: {isLoading.summary ? '⏱️ загрузка...' : '✅ загружено'}</li>
            <li>Счета: {isLoading.accounts ? '⏱️ загрузка...' : '✅ загружено'}</li>
          </ul>
        </div>
        
        {#if loadErrors.expenses || loadErrors.summary || loadErrors.accounts}
          <div class="errors">
            <h4>Ошибки:</h4>
            {#if loadErrors.expenses}
              <div class="error-item">Расходы: {loadErrors.expenses.message}</div>
            {/if}
            {#if loadErrors.summary}
              <div class="error-item">Сводка: {loadErrors.summary.message}</div>
            {/if}
            {#if loadErrors.accounts}
              <div class="error-item">Счета: {loadErrors.accounts.message}</div>
            {/if}
          </div>
        {/if}
        
        <div>
          <h4>Данные:</h4>
          <ul>
            <li>Расходы: {expenses.length} записей</li>
            <li>Сводка: {summary.length} записей</li>
            <li>Счета: {accounts.length} записей</li>
          </ul>
        </div>
        
        <button on:click={refresh}>Обновить данные</button>
      </div>
    </details>
  </div>
  
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
  .debug-panel {
    margin-bottom: 1rem;
    background-color: #f8f9fa;
    border-radius: 5px;
    font-size: 0.9rem;
  }
  .debug-panel summary {
    padding: 0.5rem;
    cursor: pointer;
    background-color: #e9ecef;
    border-radius: 5px;
  }
  .debug-content {
    padding: 1rem;
  }
  .debug-content button {
    background-color: #0d6efd;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 0.5rem;
  }
  .errors {
    background-color: #f8d7da;
    border: 1px solid #f5c2c7;
    border-radius: 4px;
    padding: 0.5rem;
    margin-bottom: 1rem;
  }
  .error-item {
    color: #842029;
    margin-bottom: 0.3rem;
  }
</style>
