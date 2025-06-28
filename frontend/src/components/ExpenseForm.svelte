<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { showAlert, showPrompt } from '../lib/dialog.js';
  import type { Category, Account } from '../lib/types';

  const dispatch = createEventDispatcher();

  let amount: string = '';
  let description: string = '';
  let category_id: string = '';
  let categories: Category[] = [];
  let accounts: Account[] = [];
  let account_id: string = '';

  const loadData = async () => {
    const resCat = await fetch('/api/categories/');
    categories = await resCat.json();
    const resAcc = await fetch('/api/accounts/');
    accounts = await resAcc.json();
  };

  onMount(loadData);

  const addExpense = async () => {
    const res = await fetch('/api/expenses/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, description, category_id: category_id || null, account_id }),
    });
    if (res.ok) {
      amount = description = category_id = account_id = '';
      dispatch('add');
    } else {
      const err = await res.json().catch(() => ({}));
      await showAlert(err.detail || 'Ошибка при добавлении расхода');
    }
  };
  // --- helpers to add new category / account ---
  const addCategory = async () => {
    const name = await showPrompt('Название новой категории:');
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
      await showAlert('Не удалось создать категорию');
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
      const acc = await res.json();
      await loadData();
      account_id = acc.id;
    } else {
      await showAlert('Не удалось создать счёт');
    }
  };

  const handleCategoryChange = (e: Event) => {
    if ((e.target as HTMLSelectElement).value === '__new__') {
      addCategory();
      category_id = '';
    }
  };

  const handleAccountChange = (e: Event) => {
    if ((e.target as HTMLSelectElement).value === '__new__') {
      addAccount();
      account_id = '';
    }
  };
</script>

<form on:submit|preventDefault={addExpense}>
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
  <button type="submit">Добавить</button>
</form>

<style>
  form {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  input, button, select {
    padding: 0.5rem;
    font-size: 1rem;
  }
</style>
