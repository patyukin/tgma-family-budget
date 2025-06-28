<script lang="ts">
  import ExpenseForm from './ExpenseForm.svelte';
  import ExpensesList from './ExpensesList.svelte';
  import Summary from './Summary.svelte';
  import type { Expense, SummaryItem } from '../lib/types';
  
  export let expenses: Expense[] = [];
  export let summary: SummaryItem[] = [];
  export let refreshGlobal: () => Promise<void>;
</script>

<ExpenseForm on:add={refreshGlobal} />
<h2>Последние траты</h2>
<ExpensesList {expenses}/>
<h2>Сводка по категориям</h2>
<Summary {summary}/>
