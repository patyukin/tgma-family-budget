import os
import pytest
import requests
import json
from datetime import datetime, timedelta

API_URL = os.environ.get('API_URL', 'http://localhost:8000')

# Хранение данных тестов для их использования между различными тестовыми функциями
class TestData:
    account_id = None
    category_id = None
    expense_id = None
    income_id = None


def test_health_check():
    """Проверка, что API сервер работает"""
    response = requests.get(f"{API_URL}/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_get_account():
    """Создание счёта и последующее его получение"""
    # Создаём счёт
    account_data = {
        "name": "Интеграционный тестовый счёт",
        "balance": 5000.0
    }
    response = requests.post(f"{API_URL}/api/accounts/", json=account_data)
    assert response.status_code == 200
    created_account = response.json()
    TestData.account_id = created_account["id"]
    
    # Запрашиваем созданный счёт
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    assert response.status_code == 200
    account = response.json()
    assert account["name"] == account_data["name"]
    assert float(account["balance"]) == account_data["balance"]


def test_create_and_get_category():
    """Создание категории и последующее её получение"""
    # Создаём категорию
    category_data = {"name": "Интеграционная тестовая категория"}
    response = requests.post(f"{API_URL}/api/categories/", json=category_data)
    assert response.status_code == 200
    created_category = response.json()
    TestData.category_id = created_category["id"]
    
    # Запрашиваем созданную категорию
    response = requests.get(f"{API_URL}/api/categories/{TestData.category_id}")
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == category_data["name"]


def test_create_expense_and_verify_balance():
    """Создание расхода и проверка изменения баланса счёта"""
    # Получаем начальный баланс счёта
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_before = response.json()
    initial_balance = float(account_before["balance"])
    
    # Создаём расход
    expense_data = {
        "description": "Интеграционный тестовый расход",
        "amount": 1000.0,
        "spent_at": datetime.now().strftime("%Y-%m-%d"),
        "category_id": TestData.category_id,
        "account_id": TestData.account_id
    }
    
    response = requests.post(f"{API_URL}/api/expenses/", json=expense_data)
    assert response.status_code == 200
    created_expense = response.json()
    TestData.expense_id = created_expense["id"]
    
    # Проверяем, что баланс счёта уменьшился
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_after = response.json()
    new_balance = float(account_after["balance"])
    assert new_balance == initial_balance - expense_data["amount"]


def test_create_income_and_verify_balance():
    """Создание дохода и проверка изменения баланса счёта"""
    # Получаем начальный баланс счёта
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_before = response.json()
    initial_balance = float(account_before["balance"])
    
    # Создаём доход
    income_data = {
        "description": "Интеграционный тестовый доход",
        "amount": 2000.0,
        "received_at": datetime.now().strftime("%Y-%m-%d"),
        "category_id": TestData.category_id,
        "account_id": TestData.account_id
    }
    
    response = requests.post(f"{API_URL}/api/incomes/", json=income_data)
    assert response.status_code == 200
    created_income = response.json()
    TestData.income_id = created_income["id"]
    
    # Проверяем, что баланс счёта увеличился
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_after = response.json()
    new_balance = float(account_after["balance"])
    assert new_balance == initial_balance + income_data["amount"]


def test_get_expense_summary():
    """Проверка получения сводки по расходам"""
    current_month = datetime.now().strftime("%Y-%m")
    response = requests.get(f"{API_URL}/api/expenses/summary/{current_month}")
    assert response.status_code == 200
    
    summary = response.json()
    # Проверяем, что в сводке есть наша тестовая категория
    category_found = False
    for item in summary:
        if item["category"] == "Интеграционная тестовая категория":
            category_found = True
            assert float(item["total"]) >= 1000.0  # Не менее нашего тестового расхода
            break
    
    assert category_found, "Тестовая категория не найдена в сводке расходов"


def test_delete_expense_and_verify_balance():
    """Удаление расхода и проверка восстановления баланса"""
    # Получаем начальный баланс счёта
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_before = response.json()
    initial_balance = float(account_before["balance"])
    
    # Запрашиваем данные о расходе
    response = requests.get(f"{API_URL}/api/expenses/{TestData.expense_id}")
    expense = response.json()
    expense_amount = float(expense["amount"])
    
    # Удаляем расход
    response = requests.delete(f"{API_URL}/api/expenses/{TestData.expense_id}")
    assert response.status_code == 200
    
    # Проверяем, что баланс счёта восстановился
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_after = response.json()
    new_balance = float(account_after["balance"])
    assert new_balance == initial_balance + expense_amount


def test_delete_income_and_verify_balance():
    """Удаление дохода и проверка восстановления баланса"""
    # Получаем начальный баланс счёта
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_before = response.json()
    initial_balance = float(account_before["balance"])
    
    # Запрашиваем данные о доходе
    response = requests.get(f"{API_URL}/api/incomes/{TestData.income_id}")
    income = response.json()
    income_amount = float(income["amount"])
    
    # Удаляем доход
    response = requests.delete(f"{API_URL}/api/incomes/{TestData.income_id}")
    assert response.status_code == 200
    
    # Проверяем, что баланс счёта уменьшился на сумму дохода
    response = requests.get(f"{API_URL}/api/accounts/{TestData.account_id}")
    account_after = response.json()
    new_balance = float(account_after["balance"])
    assert new_balance == initial_balance - income_amount


def test_cleanup():
    """Очистка тестовых данных"""
    # Удаляем созданный счёт
    response = requests.delete(f"{API_URL}/api/accounts/{TestData.account_id}")
    assert response.status_code == 200
    
    # Удаляем созданную категорию
    response = requests.delete(f"{API_URL}/api/categories/{TestData.category_id}")
    assert response.status_code == 200
