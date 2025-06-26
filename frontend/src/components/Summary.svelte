<script>
  export let summary = [];
</script>

<table>
  <thead>
    <tr>
      <th>Категория</th>
      <th>Всего</th>
    </tr>
  </thead>
  <tbody>
    {#each summary as s}
      <tr>
        <td>{s.category}</td>
        <td>{s.total}</td>
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
