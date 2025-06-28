<script lang="ts">
  import type { Account } from '../lib/types';
  export let accounts: Account[] = [];
  export let onDeposit: (acc: Account) => void;
</script>

<table>
  <thead>
    <tr>
      <th>Счёт</th>
      <th>Баланс</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    {#each accounts as acc}
      <tr>
        <td>{acc.name}</td>
        <td>{acc.balance}</td>
        <td><button on:click={() => onDeposit(acc)}>+ Пополнить</button></td>
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
    text-align:left;
    padding: 0.5rem;
    border: 1px solid #ccc;
  }
  th {
    background: #f0f0f0;
  }
  button {
    padding: 0.25rem 0.5rem;
    cursor: pointer;
  }
</style>
