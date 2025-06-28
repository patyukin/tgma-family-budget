#!/bin/sh

echo "Ждем, пока backend_test:8000 станет доступен..."
until $(curl --output /dev/null --silent --fail http://backend_test:8000/api/health); do
  echo "Ждем доступности API..."
  sleep 1
done

echo "API доступен! Запускаем тесты..."
exec pytest -xvs tests/integration/
