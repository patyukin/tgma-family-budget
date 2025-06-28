import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import ModalDialog from './ModalDialog.svelte';
import { dialog } from '../lib/dialog.js';
import { get } from 'svelte/store';

// Мокаем свелт-стор
vi.mock('../lib/dialog.js', () => {
  const { writable } = require('svelte/store');
  const dialogStore = writable({
    visible: false,
    type: 'alert',
    message: '',
    resolve: vi.fn(),
    defaultValue: undefined,
  });
  
  return {
    dialog: dialogStore,
    showAlert: vi.fn(),
    showPrompt: vi.fn(),
  };
});

describe('ModalDialog', () => {
  beforeEach(() => {
    // Сбрасываем стор перед каждым тестом
    dialog.set({
      visible: false,
      type: 'alert',
      message: '',
      resolve: vi.fn(),
      defaultValue: undefined,
    });
  });

  it('не отображается, когда visible=false', () => {
    render(ModalDialog);
    const modal = document.querySelector('.modal');
    expect(modal).not.toBeVisible();
  });

  it('отображается с сообщением, когда visible=true', () => {
    dialog.set({
      visible: true,
      type: 'alert',
      message: 'Тестовое сообщение',
      resolve: vi.fn(),
      defaultValue: undefined,
    });
    
    render(ModalDialog);
    expect(screen.getByText('Тестовое сообщение')).toBeInTheDocument();
  });

  it('вызывает resolve и закрывает диалог при нажатии на OK', async () => {
    const mockResolve = vi.fn();
    
    dialog.set({
      visible: true,
      type: 'alert',
      message: 'Тестовое сообщение',
      resolve: mockResolve,
      defaultValue: undefined,
    });
    
    render(ModalDialog);
    const okButton = screen.getByText('OK');
    
    await fireEvent.click(okButton);
    
    expect(mockResolve).toHaveBeenCalled();
    expect(get(dialog).visible).toBe(false);
  });

  it('в prompt режиме показывает поле ввода и передает его значение в resolve', async () => {
    const mockResolve = vi.fn();
    
    dialog.set({
      visible: true,
      type: 'prompt',
      message: 'Введите значение',
      resolve: mockResolve,
      defaultValue: 'Значение по умолчанию',
    });
    
    render(ModalDialog);
    const input = screen.getByDisplayValue('Значение по умолчанию');
    expect(input).toBeInTheDocument();
    
    // Изменяем значение в поле ввода
    await fireEvent.change(input, { target: { value: 'Новое значение' } });
    
    // Нажимаем кнопку OK
    const okButton = screen.getByText('OK');
    await fireEvent.click(okButton);
    
    // Проверяем, что resolve вызван с новым значением
    expect(mockResolve).toHaveBeenCalledWith('Новое значение');
    expect(get(dialog).visible).toBe(false);
  });

  it('при нажатии на Отмена закрывает диалог и передает null', async () => {
    const mockResolve = vi.fn();
    
    dialog.set({
      visible: true,
      type: 'prompt',
      message: 'Введите значение',
      resolve: mockResolve,
      defaultValue: '',
    });
    
    render(ModalDialog);
    const cancelButton = screen.getByText('Отмена');
    
    await fireEvent.click(cancelButton);
    
    expect(mockResolve).toHaveBeenCalledWith(null);
    expect(get(dialog).visible).toBe(false);
  });
});
