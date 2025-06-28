<script lang="ts">
  import type { Expense } from '../lib/types';
  export let expenses: Expense[] = [];
</script>

<table>
  <thead>
    <tr>
      <th>Дата</th>
      <th>Категория</th>
      <th>Описание</th>
      <th>Сумма</th>
    </tr>
  </thead>
  <tbody>
    {#each expenses as exp}
      <tr>
        <td>{new Date(exp.spent_at).toLocaleDateString()}</td>
        <td>{exp.category?.name ?? '-'}</td>
        <td>{exp.description}</td>
        <td>{exp.amount}</td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    padding: 0.5rem;
    border: 1px solid #ccc;
  }
  th {
    background: #f0f0f0;
  }
</style>
