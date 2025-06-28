FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей, включая curl для healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Изменяем разрешения на выполнение для скриптов
RUN chmod +x /app/wait-for-postgres.sh || echo "wait-for-postgres.sh not found"

# Настройка переменных окружения для тестов
ENV DATABASE_URL="postgresql+asyncpg://postgres:postgres@postgres_test:5432/budget_test"
ENV ENVIRONMENT="test"

EXPOSE 8000

# Запуск API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
