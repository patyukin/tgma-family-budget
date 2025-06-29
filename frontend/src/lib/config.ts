/**
 * Конфигурация приложения
 */

// Расширение интерфейса ImportMeta для Vite переменных окружения
interface ImportMetaEnv {
  readonly PROD: boolean;
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Базовый URL для API запросов
// В режиме разработки используем относительный путь (будет проксироваться через Vite)
// В продакшене используем значение из переменной окружения или дефолтное значение
export const API_BASE_URL = import.meta.env.PROD 
  ? import.meta.env.VITE_API_URL
  : '';
