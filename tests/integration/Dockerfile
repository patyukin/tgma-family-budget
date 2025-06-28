FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y curl && apt-get clean

# Копирование и установка зависимостей для интеграционных тестов
COPY tests/integration/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Копирование тестов
COPY tests/ /app/tests/

# Предоставляем права на выполнение скрипта запуска тестов
RUN chmod +x /app/tests/integration/run_tests.sh

# Запускаем тесты после проверки доступности бэкенда
CMD ["/app/tests/integration/run_tests.sh"]
