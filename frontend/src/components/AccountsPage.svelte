<script lang="ts">
  import { onMount } from 'svelte';
  import { showAlert, showPrompt } from '../lib/dialog.js';
  import AccountsList from './AccountsList.svelte';
  import type { Account } from '../lib/types';

  export let refreshGlobal;

  let accounts: Account[] = [];
  const loadAccounts = async () => {
    try {
      const res = await fetch('/api/accounts');
      if (res.ok) {
        accounts = await res.json();
      } else {
        console.error('Ошибка загрузки счетов:', res.status);
        await showAlert('Не удалось загрузить счета');
      }
    } catch (error) {
      console.error('Ошибка при загрузке счетов:', error);
      await showAlert('Ошибка соединения с сервером');
    }
  };
  onMount(loadAccounts);

  const handleDeposit = async (acc: Account) => {
    const amtStr = await showPrompt(`Сколько зачислить на «${acc.name}»?`, '0');
    if (!amtStr) return;
    const amount = parseFloat(amtStr);
    if (!amount || amount<=0) { await showAlert('Некорректная сумма'); return; }
    const res = await fetch('/api/incomes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, account_id: acc.id, description: 'Пополнение' })
    });
    if (res.ok) {
      await loadAccounts();
      refreshGlobal && refreshGlobal();
    } else {
      await showAlert('Не удалось зачислить средства');
    }
  };

  const addAccount = async () => {
    const name = await showPrompt('Название счёта:');
    if (!name) return;
    const balStr = await showPrompt('Начальный баланс:', '0');
    if (balStr === null) return;
    const balance = parseFloat(balStr) || 0;

    const res = await fetch('/api/accounts/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, balance })
    });
    if (res.ok) {
      await loadAccounts();
      refreshGlobal && refreshGlobal();
    } else {
      const err = await res.json().catch(() => ({}));
      await showAlert(err.detail || 'Не удалось создать счёт');
    }
  };
</script>

<button on:click={addAccount} style="margin-bottom:0.5rem">+ Новый счёт</button>
<AccountsList {accounts} onDeposit={handleDeposit} />
