import { writable } from 'svelte/store';

/**
 * @typedef {Object} DialogState
 * @property {boolean} visible
 * @property {'alert'|'prompt'} type
 * @property {string} message
 * @property {(value:any)=>void|undefined} [resolve]
 * @property {string|undefined} [defaultValue]
 */

// Global dialog store
/** @type {import('svelte/store').Writable<DialogState>} */
export const dialog = writable(/** @type {DialogState} */({
  visible: false,
  type: 'alert',
  message: '',
  resolve: undefined,
  defaultValue: undefined,
}));

/**
 * Показать модальное окно типа alert (только кнопка ОК)
 * @param {string} message
 * @param {string} [def=undefined]
 * @returns {Promise<void>}
 */
export function showAlert(message, def = undefined) {
  return new Promise((resolve) => {
    dialog.set({
      visible: true,
      type: 'alert',
      message,
      defaultValue: def,
      resolve,
    });
  });
}

/**
 * Показать модальное окно типа prompt (поле ввода, кнопка ОК/Отмена)
 * @param {string} message
 * @param {string} [def='']
 * @returns {Promise<string|null>} введённое значение или null при отмене
 */
export function showPrompt(message, def = '') {
  return new Promise((resolve) => {
    dialog.set({
      visible: true,
      type: 'prompt',
      message,
      defaultValue: def,
      resolve,
    });
  });
}
