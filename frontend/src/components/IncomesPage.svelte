<script>
  import IncomeForm from './IncomeForm.svelte';

  export let refreshGlobal;
</script>

<IncomeForm on:add={refreshGlobal} />
