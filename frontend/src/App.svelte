<script>
  import { onMount } from 'svelte';
  import ExpenseForm from './components/ExpenseForm.svelte';
  import ExpensesList from './components/ExpensesList.svelte';
  import Summary from './components/Summary.svelte';

  let expenses = [];
  let summary = [];

  const loadExpenses = async () => {
    const res = await fetch('/api/expenses');
    expenses = await res.json();
  };
  const loadSummary = async () => {
    const res = await fetch('/api/expenses/summary');
    summary = await res.json();
  };

  const refresh = async () => {
    await loadExpenses();
    await loadSummary();
  };

  onMount(refresh);
</script>

<main>
  <h1>Семейный бюджет</h1>
  <ExpenseForm on:add={refresh} />
  <h2>Последние траты</h2>
  <ExpensesList {expenses} />
  <h2>Сводка по категориям</h2>
  <Summary {summary} />
</main>

<style>
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
    font-family: Arial, sans-serif;
  }
</style>
