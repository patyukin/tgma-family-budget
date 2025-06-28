import os
import pytest
import requests
from datetime import datetime, timedelta

API_URL = os.environ.get('API_URL', 'http://localhost:8000')


def test_complete_business_flow():
    """
    Комплексный интеграционный тест, проверяющий типичный пользовательский сценарий:
    1. Создание категорий расходов и доходов
    2. Создание нескольких счетов
    3. Регистрация расходов разных категорий
    4. Регистрация доходов
    5. Проверка корректного подсчета баланса
    6. Проверка сводок по категориям
    """
    # ======= 1. Создание категорий =======
    categories = [
        {"name": "Продукты"},
        {"name": "Транспорт"},
        {"name": "Коммунальные услуги"},
        {"name": "Развлечения"},
        {"name": "Зарплата"},
        {"name": "Подработка"}
    ]
    
    category_ids = {}
    for category in categories:
        response = requests.post(f"{API_URL}/api/categories/", json=category)
        assert response.status_code == 200
        result = response.json()
        category_ids[category["name"]] = result["id"]
    
    # Проверяем, что все категории созданы
    response = requests.get(f"{API_URL}/api/categories/")
    assert response.status_code == 200
    all_categories = response.json()
    assert len(all_categories) >= len(categories)
    
    # ======= 2. Создание счетов =======
    accounts = [
        {"name": "Наличные", "balance": 15000},
        {"name": "Дебетовая карта", "balance": 25000},
        {"name": "Сберегательный счет", "balance": 50000}
    ]
    
    account_ids = {}
    for account in accounts:
        response = requests.post(f"{API_URL}/api/accounts/", json=account)
        assert response.status_code == 200
        result = response.json()
        account_ids[account["name"]] = result["id"]
        assert float(result["balance"]) == account["balance"]
    
    # Проверяем, что все счета созданы
    response = requests.get(f"{API_URL}/api/accounts/")
    assert response.status_code == 200
    all_accounts = response.json()
    assert len(all_accounts) >= len(accounts)
    
    # ======= 3. Регистрация расходов =======
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    expenses = [
        {
            "description": "Покупка продуктов в магазине",
            "amount": 2500,
            "spent_at": today.strftime("%Y-%m-%d"),
            "category_id": category_ids["Продукты"],
            "account_id": account_ids["Наличные"]
        },
        {
            "description": "Проезд на метро",
            "amount": 300,
            "spent_at": today.strftime("%Y-%m-%d"),
            "category_id": category_ids["Транспорт"],
            "account_id": account_ids["Дебетовая карта"]
        },
        {
            "description": "Оплата электроэнергии",
            "amount": 1200,
            "spent_at": yesterday.strftime("%Y-%m-%d"),
            "category_id": category_ids["Коммунальные услуги"],
            "account_id": account_ids["Дебетовая карта"]
        },
        {
            "description": "Билеты в кино",
            "amount": 1000,
            "spent_at": day_before.strftime("%Y-%m-%d"),
            "category_id": category_ids["Развлечения"],
            "account_id": account_ids["Дебетовая карта"]
        },
    ]
    
    # Сохраняем ожидаемые балансы счетов
    expected_balances = {
        "Наличные": 15000 - 2500,  # Начальный баланс - расход на продукты
        "Дебетовая карта": 25000 - (300 + 1200 + 1000),  # Начальный баланс - сумма расходов
        "Сберегательный счет": 50000  # Без изменений
    }
    
    for expense in expenses:
        response = requests.post(f"{API_URL}/api/expenses/", json=expense)
        assert response.status_code == 200
    
    # Проверяем, что баланс счетов обновился правильно
    for account_name, expected_balance in expected_balances.items():
        response = requests.get(f"{API_URL}/api/accounts/{account_ids[account_name]}")
        assert response.status_code == 200
        account = response.json()
        assert float(account["balance"]) == expected_balance
    
    # ======= 4. Регистрация доходов =======
    incomes = [
        {
            "description": "Зарплата за месяц",
            "amount": 70000,
            "received_at": today.strftime("%Y-%m-%d"),
            "category_id": category_ids["Зарплата"],
            "account_id": account_ids["Дебетовая карта"]
        },
        {
            "description": "Фриланс проект",
            "amount": 15000,
            "received_at": yesterday.strftime("%Y-%m-%d"),
            "category_id": category_ids["Подработка"],
            "account_id": account_ids["Наличные"]
        }
    ]
    
    # Обновляем ожидаемые балансы счетов
    expected_balances["Дебетовая карта"] += 70000
    expected_balances["Наличные"] += 15000
    
    for income in incomes:
        response = requests.post(f"{API_URL}/api/incomes/", json=income)
        assert response.status_code == 200
    
    # Проверяем, что баланс счетов обновился правильно
    for account_name, expected_balance in expected_balances.items():
        response = requests.get(f"{API_URL}/api/accounts/{account_ids[account_name]}")
        assert response.status_code == 200
        account = response.json()
        assert float(account["balance"]) == expected_balance
    
    # ======= 5. Проверка сводки по расходам =======
    current_month = datetime.now().strftime("%Y-%m")
    response = requests.get(f"{API_URL}/api/expenses/summary/{current_month}")
    assert response.status_code == 200
    summary = response.json()
    
    # Создаем словарь категория -> сумма для проверки
    summary_dict = {item["category"]: float(item["total"]) for item in summary}
    
    # Проверяем суммы расходов по категориям
    assert summary_dict["Продукты"] == 2500
    assert summary_dict["Транспорт"] == 300
    assert summary_dict["Коммунальные услуги"] == 1200
    assert summary_dict["Развлечения"] == 1000

    # ======= 6. Проверка общих сумм =======
    # Получаем список всех расходов
    response = requests.get(f"{API_URL}/api/expenses/")
    assert response.status_code == 200
    all_expenses = response.json()
    
    # Проверяем, что количество расходов соответствует ожидаемому
    assert len(all_expenses) >= len(expenses)
    
    # Получаем список всех доходов
    response = requests.get(f"{API_URL}/api/incomes/")
    assert response.status_code == 200
    all_incomes = response.json()
    
    # Проверяем, что количество доходов соответствует ожидаемому
    assert len(all_incomes) >= len(incomes)
    
    # ======= 7. Очистка тестовых данных =======
    # Удаляем все созданные доходы
    for income in all_incomes:
        response = requests.delete(f"{API_URL}/api/incomes/{income['id']}")
        assert response.status_code == 200
    
    # Удаляем все созданные расходы
    for expense in all_expenses:
        response = requests.delete(f"{API_URL}/api/expenses/{expense['id']}")
        assert response.status_code == 200
    
    # Удаляем все созданные счета
    for account_id in account_ids.values():
        response = requests.delete(f"{API_URL}/api/accounts/{account_id}")
        assert response.status_code == 200
    
    # Удаляем все созданные категории
    for category_id in category_ids.values():
        response = requests.delete(f"{API_URL}/api/categories/{category_id}")
        assert response.status_code == 200
