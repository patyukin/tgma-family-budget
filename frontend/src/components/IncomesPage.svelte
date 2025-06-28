<script lang="ts">
  import IncomeForm from './IncomeForm.svelte';

  export let refreshGlobal: () => Promise<void>;
</script>

<IncomeForm on:add={refreshGlobal} />
