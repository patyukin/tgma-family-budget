#!/bin/bash

# Остановка и удаление существующих контейнеров тестовой среды
docker compose -f docker-compose.test.yml down -v

# Запуск тестовой среды в контейнерах
docker compose -f docker-compose.test.yml up --build --exit-code-from tests

# Получение кода выхода тестов
TEST_EXIT_CODE=$?

# Уборка за собой
docker compose -f docker-compose.test.yml down -v

# Выходим с тем же кодом, что и тесты
exit $TEST_EXIT_CODE
