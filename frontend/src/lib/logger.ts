/**
 * Утилита для логирования с разными уровнями и форматированием
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

// Текущий уровень логирования (можно менять через localStorage)
const getCurrentLogLevel = (): LogLevel => {
  try {
    const savedLevel = localStorage.getItem('fb_log_level');
    return savedLevel ? parseInt(savedLevel, 10) : LogLevel.INFO;
  } catch {
    return LogLevel.INFO;
  }
};

// Цвета для разных уровней логирования
const LOG_COLORS = {
  [LogLevel.DEBUG]: 'color: #6c757d',
  [LogLevel.INFO]: 'color: #0d6efd',
  [LogLevel.WARN]: 'color: #ffc107',
  [LogLevel.ERROR]: 'color: #dc3545'
};

// Префиксы для разных уровней логирования
const LOG_PREFIXES = {
  [LogLevel.DEBUG]: '[DEBUG]',
  [LogLevel.INFO]: '[INFO]',
  [LogLevel.WARN]: '[WARN]',
  [LogLevel.ERROR]: '[ERROR]'
};

/**
 * Базовая функция логирования
 */
export const log = (level: LogLevel, message: string, ...args: any[]): void => {
  const currentLevel = getCurrentLogLevel();
  
  if (level >= currentLevel) {
    const prefix = LOG_PREFIXES[level];
    const color = LOG_COLORS[level];
    const timestamp = new Date().toISOString();
    
    console.log(
      `%c${prefix} [${timestamp}] ${message}`,
      color,
      ...args
    );
  }
};

// Удобные методы для разных уровней логирования
export const debug = (message: string, ...args: any[]): void => log(LogLevel.DEBUG, message, ...args);
export const info = (message: string, ...args: any[]): void => log(LogLevel.INFO, message, ...args);
export const warn = (message: string, ...args: any[]): void => log(LogLevel.WARN, message, ...args);
export const error = (message: string, ...args: any[]): void => log(LogLevel.ERROR, message, ...args);

/**
 * Логирование API запросов
 */
export const logApiRequest = (method: string, url: string, options?: RequestInit): void => {
  debug(`API Request: ${method} ${url}`, { options });
};

/**
 * Логирование API ответов
 */
export const logApiResponse = async (response: Response, url: string): Promise<any> => {
  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');
  
  if (isJson) {
    try {
      // Клонируем ответ, чтобы не израсходовать body
      const clone = response.clone();
      const data = await clone.json();
      debug(`API Response: ${url}`, { status: response.status, data });
      return data;
    } catch (err) {
      error(`Failed to parse JSON from ${url}`, err);
      throw err;
    }
  } else {
    const text = await response.clone().text();
    warn(`Non-JSON response from ${url}`, { 
      status: response.status, 
      contentType,
      text: text.substring(0, 200) + (text.length > 200 ? '...' : '')
    });
    return response;
  }
};
