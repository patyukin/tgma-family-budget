<script>
  import { onMount } from 'svelte';
  import AccountsList from './AccountsList.svelte';
  export let refreshGlobal;

  let accounts = [];
  const loadAccounts = async () => {
    accounts = await (await fetch('/api/accounts/')).json();
  };
  onMount(loadAccounts);

  const handleDeposit = async (acc) => {
    const amtStr = prompt(`Сколько зачислить на «${acc.name}»?`, '0');
    if (!amtStr) return;
    const amount = parseFloat(amtStr);
    if (!amount || amount<=0) return alert('Некорректная сумма');
    const res = await fetch('/api/incomes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, account_id: acc.id, description: 'Пополнение' })
    });
    if (res.ok) {
      await loadAccounts();
      refreshGlobal && refreshGlobal();
    } else {
      alert('Не удалось зачислить средства');
    }
  };

  const addAccount = async () => {
    const name = prompt('Название счёта:');
    if (!name) return;
    const balStr = prompt('Начальный баланс:', '0');
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
      alert(err.detail || 'Не удалось создать счёт');
    }
  };
</script>

<button on:click={addAccount} style="margin-bottom:0.5rem">+ Новый счёт</button>
<AccountsList {accounts} onDeposit={handleDeposit} />
