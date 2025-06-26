<script>
  import { createEventDispatcher, onMount } from 'svelte';

  const dispatch = createEventDispatcher();

  let amount = '';
  let description = '';
  let category_id = '';
  let account_id = '';
  let categories = [];
  let accounts = [];

  const loadData = async () => {
    categories = await (await fetch('/api/categories/')).json();
    accounts = await (await fetch('/api/accounts/')).json();
  };
  onMount(loadData);

  const addIncome = async () => {
    const res = await fetch('/api/incomes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, description, category_id: category_id || null, account_id }),
    });
    if (res.ok) {
      amount = description = category_id = account_id = '';
      dispatch('add');
    } else {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || 'Ошибка при добавлении дохода');
    }
  };
  // --- helpers to add new category / account ---
  const addCategory = async () => {
    const name = prompt('Название новой категории:');
    if (!name) return;
    const res = await fetch('/api/categories/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    if (res.ok) {
      const cat = await res.json();
      await loadData();
      category_id = cat.id;
    } else {
      alert('Не удалось создать категорию');
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
      const acc = await res.json();
      await loadData();
      account_id = acc.id;
    } else {
      alert('Не удалось создать счёт');
    }
  };

  const handleCategoryChange = (e) => {
    if (e.target.value === '__new__') {
      addCategory();
      category_id = '';
    }
  };

  const handleAccountChange = (e) => {
    if (e.target.value === '__new__') {
      addAccount();
      account_id = '';
    }
  };
</script>

<form on:submit|preventDefault={addIncome} style="margin-bottom:1rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
  <input required type="number" step="0.01" placeholder="Сумма" bind:value={amount} />
  <input type="text" placeholder="Описание" bind:value={description} />
  <select bind:value={category_id} on:change={handleCategoryChange}>
    <option value="">Без категории</option>
    <option value="__new__">+ Новая категория</option>
    {#each categories as cat}
      <option value={cat.id}>{cat.name}</option>
    {/each}
  </select>
  <select bind:value={account_id} required on:change={handleAccountChange}>
    <option value="" disabled selected>Счёт</option>
    <option value="__new__">+ Новый счёт</option>
    {#each accounts as acc}
      <option value={acc.id}>{acc.name} ({acc.balance})</option>
    {/each}
  </select>
  <button type="submit">Добавить доход</button>
</form>
