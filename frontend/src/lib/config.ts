/**
 * Конфигурация приложения
 */

// Расширение интерфейса ImportMeta для Vite переменных окружения
interface ImportMetaEnv {
  readonly PROD: boolean;
  readonly VITE_APP_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Базовый URL для API запросов
// В режиме разработки используем относительный путь (будет проксироваться через Vite)
// В продакшене используем значение из переменной окружения или дефолтное значение
export const API_BASE_URL = import.meta.env.PROD 
  ? import.meta.env.VITE_APP_API_URL
  : '';

// --- Глобальный патч fetch, чтобы всегда подставлять API_BASE_URL в production ---
if (import.meta.env.PROD && typeof window !== 'undefined') {
  const originalFetch = window.fetch.bind(window);

  window.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    let url: string;

    if (typeof input === 'string') {
      url = input;
    } else if (input instanceof Request) {
      url = input.url;
    } else if (input instanceof URL) {
      url = input.toString();
    } else {
      // fallback to original
      // @ts-ignore
      return originalFetch(input, init);
    }

    if (url.startsWith('/api/')) {
      const fullUrl = `${API_BASE_URL}${url}`;
      if (typeof input === 'string') {
        input = fullUrl;
      } else if (input instanceof Request) {
        input = new Request(fullUrl, input);
      } else {
        input = new URL(fullUrl);
      }
    }

    // @ts-ignore – типы совпадают
    return originalFetch(input, init);
  };
}
