<script>
  import { onMount } from 'svelte';

  let categories = [];

  const loadCategories = async () => {
    categories = await (await fetch('/api/categories/')).json();
  };
  onMount(loadCategories);
</script>

<h2>Категории</h2>
<ul>
  {#each categories as cat}
    <li>{cat.name}</li>
  {/each}
</ul>

<style>
  ul {
    list-style: none;
    padding: 0;
  }
  li {
    padding: 0.25rem 0;
  }
</style>
