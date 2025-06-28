<script>
import { dialog } from '../lib/dialog.js';
import { onDestroy } from 'svelte';

/** @type {import('../lib/dialog.js').DialogState} */
let state;
const unsubscribe = dialog.subscribe(v => state = v);

onDestroy(unsubscribe);

const close = () => {
  if (state && state.resolve) state.resolve(null);
  dialog.set({ ...state, visible: false });
};

const ok = () => {
  if (state && state.resolve) {
    if (state.type === 'prompt') {
      state.resolve(inputValue);
    } else {
      state.resolve(undefined);
    }
  }
  dialog.set({ ...state, visible: false });
};

let inputValue = '';
$: if (state && state.defaultValue !== undefined) inputValue = state.defaultValue;
</script>

{#if state?.visible}
  <div class="overlay">
    <div class="modal">
      <p>{state.message}</p>
      {#if state.type === 'prompt'}
        <!-- svelte-ignore a11y-autofocus -->
        <input bind:value={inputValue} autofocus />
      {/if}
      <div class="actions">
        <button on:click={ok}>OK</button>
        {#if state.type === 'prompt'}
          <button on:click={close}>Отмена</button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 4px;
  max-width: 90vw;
  min-width: 260px;
}
.actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
input {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.5rem;
}
</style>
