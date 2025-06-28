import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.models import Income, Category, Account


@pytest.mark.asyncio
async def test_create_income(test_client, test_db):
    # Создаём необходимые зависимости: категорию и счёт
    test_category = Category(name="Зарплата")
    test_account = Account(name="Дебетовая карта", balance=Decimal("1000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        category_id = test_category.id
        account_id = test_account.id
    
    # Подготавливаем данные для создания дохода
    income_data = {
        "description": "Зарплата за июнь",
        "amount": 50000.0,
        "received_at": datetime.now().strftime("%Y-%m-%d"),
        "category_id": category_id,
        "account_id": account_id
    }
    
    # Отправляем запрос на создание дохода
    response = test_client.post("/api/incomes/", json=income_data)
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    created_income = response.json()
    assert created_income["description"] == income_data["description"]
    assert float(created_income["amount"]) == income_data["amount"]
    assert "id" in created_income
    
    # Проверяем, что баланс счёта увеличился
    response = test_client.get(f"/api/accounts/{account_id}")
    account = response.json()
    assert float(account["balance"]) == 51000.0  # Начальный баланс + сумма дохода


@pytest.mark.asyncio
async def test_get_all_incomes(test_client, test_db):
    # Создаём необходимые зависимости
    test_category = Category(name="Доходы")
    test_account = Account(name="Накопительный счёт", balance=Decimal("5000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        category_id = test_category.id
        account_id = test_account.id
        
        # Создаём несколько тестовых доходов напрямую через ORM
        test_incomes = [
            Income(
                description="Подработка",
                amount=Decimal("15000.0"),
                received_at=datetime.now().date(),
                category_id=category_id,
                account_id=account_id
            ),
            Income(
                description="Возврат долга",
                amount=Decimal("5000.0"),
                received_at=datetime.now().date() - timedelta(days=1),
                category_id=category_id,
                account_id=account_id
            ),
        ]
        test_db.add_all(test_incomes)
    
    # Запрашиваем список всех доходов
    response = test_client.get("/api/incomes/")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    incomes = response.json()
    assert len(incomes) >= 2  # Может быть больше 2, если были и другие доходы
    
    # Проверяем наличие наших доходов в ответе
    income_descriptions = [income["description"] for income in incomes]
    assert "Подработка" in income_descriptions
    assert "Возврат долга" in income_descriptions


@pytest.mark.asyncio
async def test_get_income_by_id(test_client, test_db):
    # Создаём необходимые зависимости
    test_category = Category(name="Инвестиции")
    test_account = Account(name="Инвестиционный счёт", balance=Decimal("10000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        
        # Создаём тестовый доход напрямую через ORM
        new_income = Income(
            description="Дивиденды",
            amount=Decimal("1200.50"),
            received_at=datetime.now().date(),
            category_id=test_category.id,
            account_id=test_account.id
        )
        test_db.add(new_income)
        await test_db.flush()
        income_id = new_income.id
    
    # Запрашиваем доход по ID
    response = test_client.get(f"/api/incomes/{income_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    income = response.json()
    assert income["description"] == "Дивиденды"
    assert float(income["amount"]) == 1200.50


@pytest.mark.asyncio
async def test_update_income(test_client, test_db):
    # Создаём необходимые зависимости
    test_category = Category(name="Разное")
    test_account = Account(name="Общий счёт", balance=Decimal("20000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        category_id = test_category.id
        account_id = test_account.id
        
        # Создаём тестовый доход напрямую через ORM
        original_amount = Decimal("3000.0")
        new_income = Income(
            description="Первоначальное описание",
            amount=original_amount,
            received_at=datetime.now().date(),
            category_id=category_id,
            account_id=account_id
        )
        test_db.add(new_income)
        await test_db.flush()
        income_id = new_income.id
        
        # Учитываем влияние дохода на баланс счёта
        test_account.balance += original_amount
    
    # Проверяем начальный баланс счёта
    response = test_client.get(f"/api/accounts/{account_id}")
    account_before = response.json()
    assert float(account_before["balance"]) == 23000.0
    
    # Данные для обновления
    update_data = {
        "description": "Обновлённое описание",
        "amount": 5000.0,
        "received_at": datetime.now().strftime("%Y-%m-%d"),
        "category_id": category_id,
        "account_id": account_id
    }
    
    # Отправляем запрос на обновление дохода
    response = test_client.put(f"/api/incomes/{income_id}", json=update_data)
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    updated_income = response.json()
    assert updated_income["description"] == update_data["description"]
    assert float(updated_income["amount"]) == update_data["amount"]
    
    # Проверяем, что баланс счёта обновился соответственно
    response = test_client.get(f"/api/accounts/{account_id}")
    account_after = response.json()
    assert float(account_after["balance"]) == 25000.0  # Начальный баланс - старая сумма + новая сумма


@pytest.mark.asyncio
async def test_delete_income(test_client, test_db):
    # Создаём необходимые зависимости
    test_category = Category(name="Категория для удаления")
    test_account = Account(name="Счёт для удаления дохода", balance=Decimal("5000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        
        # Создаём тестовый доход для удаления
        income_amount = Decimal("2500.0")
        new_income = Income(
            description="Доход для удаления",
            amount=income_amount,
            received_at=datetime.now().date(),
            category_id=test_category.id,
            account_id=test_account.id
        )
        test_db.add(new_income)
        await test_db.flush()
        income_id = new_income.id
        account_id = test_account.id
        
        # Учитываем, что доход уже создан и повлиял на баланс счёта
        test_account.balance += income_amount
    
    # Проверяем начальный баланс счёта
    response = test_client.get(f"/api/accounts/{account_id}")
    account_before = response.json()
    assert float(account_before["balance"]) == 7500.0
    
    # Отправляем запрос на удаление дохода
    response = test_client.delete(f"/api/incomes/{income_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    deleted_income = response.json()
    assert deleted_income["description"] == "Доход для удаления"
    
    # Проверяем, что доход действительно удалён
    response = test_client.get(f"/api/incomes/{income_id}")
    assert response.status_code == 404
    
    # Проверяем, что баланс счёта уменьшился на сумму удалённого дохода
    response = test_client.get(f"/api/accounts/{account_id}")
    account_after = response.json()
    assert float(account_after["balance"]) == 5000.0
