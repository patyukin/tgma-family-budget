<script>
  import { createEventDispatcher, onMount } from 'svelte';

  const dispatch = createEventDispatcher();

  let amount = '';
  let description = '';
  let category_id = '';
  let categories = [];

  const loadCategories = async () => {
    const res = await fetch('/api/categories/');
    categories = await res.json();
  };

  onMount(loadCategories);

  const addExpense = async () => {
    await fetch('/api/expenses/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, description, category_id: category_id || null }),
    });
    amount = description = category_id = '';
    dispatch('add');
  };
</script>

<form on:submit|preventDefault={addExpense}>
  <input required type="number" step="0.01" placeholder="Сумма" bind:value={amount} />
  <input type="text" placeholder="Описание" bind:value={description} />
  <select bind:value={category_id}>
    <option value="">Без категории</option>
    {#each categories as cat}
      <option value={cat.id}>{cat.name}</option>
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
