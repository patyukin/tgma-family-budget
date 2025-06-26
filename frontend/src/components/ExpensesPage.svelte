<script>
  import ExpenseForm from './ExpenseForm.svelte';
  import ExpensesList from './ExpensesList.svelte';
  import Summary from './Summary.svelte';
  export let expenses = [];
  export let summary = [];
  export let refreshGlobal;
</script>

<ExpenseForm on:add={refreshGlobal} />
<h2>Последние траты</h2>
<ExpensesList {expenses}/>
<h2>Сводка по категориям</h2>
<Summary {summary}/>
