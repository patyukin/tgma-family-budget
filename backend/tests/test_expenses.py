import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.models import Expense, Category, Account


@pytest.mark.asyncio
async def test_create_expense(test_client, test_db):
    # Создаём необходимые зависимости: категорию и счёт
    test_category = Category(name="Тестовая категория")
    test_account = Account(name="Тестовый счёт", balance=Decimal("5000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        category_id = test_category.id
        account_id = test_account.id
    
    # Подготавливаем данные для создания расхода
    expense_data = {
        "description": "Тестовый расход",
        "amount": 500.0,
        "spent_at": datetime.now().strftime("%Y-%m-%d"),
        "category_id": category_id,
        "account_id": account_id
    }
    
    # Отправляем запрос на создание расхода
    response = test_client.post("/api/expenses/", json=expense_data)
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    created_expense = response.json()
    assert created_expense["description"] == expense_data["description"]
    assert float(created_expense["amount"]) == expense_data["amount"]
    assert "id" in created_expense
    
    # Проверяем, что баланс счёта уменьшился
    response = test_client.get(f"/api/accounts/{account_id}")
    account = response.json()
    assert float(account["balance"]) == 4500.0


@pytest.mark.asyncio
async def test_get_all_expenses(test_client, test_db):
    # Создаём необходимые зависимости
    test_category = Category(name="Категория расходов")
    test_account = Account(name="Счёт для расходов", balance=Decimal("10000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        category_id = test_category.id
        account_id = test_account.id
        
        # Создаём несколько тестовых расходов напрямую через ORM
        test_expenses = [
            Expense(
                description="Расход 1",
                amount=Decimal("100.0"),
                spent_at=datetime.now().date(),
                category_id=category_id,
                account_id=account_id
            ),
            Expense(
                description="Расход 2",
                amount=Decimal("200.0"),
                spent_at=datetime.now().date() - timedelta(days=1),
                category_id=category_id,
                account_id=account_id
            ),
        ]
        test_db.add_all(test_expenses)
    
    # Запрашиваем список всех расходов
    response = test_client.get("/api/expenses/")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) >= 2  # Может быть больше 2, если были и другие расходы
    
    # Проверяем наличие наших расходов в ответе
    expense_descriptions = [expense["description"] for expense in expenses]
    assert "Расход 1" in expense_descriptions
    assert "Расход 2" in expense_descriptions


@pytest.mark.asyncio
async def test_get_expense_by_id(test_client, test_db):
    # Создаём необходимые зависимости
    test_category = Category(name="Ещё одна категория")
    test_account = Account(name="Ещё один счёт", balance=Decimal("5000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        
        # Создаём тестовый расход напрямую через ORM
        new_expense = Expense(
            description="Запрашиваемый расход",
            amount=Decimal("333.33"),
            spent_at=datetime.now().date(),
            category_id=test_category.id,
            account_id=test_account.id
        )
        test_db.add(new_expense)
        await test_db.flush()
        expense_id = new_expense.id
    
    # Запрашиваем расход по ID
    response = test_client.get(f"/api/expenses/{expense_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    expense = response.json()
    assert expense["description"] == "Запрашиваемый расход"
    assert float(expense["amount"]) == 333.33


@pytest.mark.asyncio
async def test_delete_expense(test_client, test_db):
    # Создаём необходимые зависимости
    test_category = Category(name="Категория для удаления")
    test_account = Account(name="Счёт для удаления расхода", balance=Decimal("3000.0"))
    
    async with test_db.begin():
        test_db.add_all([test_category, test_account])
        await test_db.flush()
        
        # Создаём тестовый расход для удаления
        expense_amount = Decimal("300.0")
        new_expense = Expense(
            description="Расход для удаления",
            amount=expense_amount,
            spent_at=datetime.now().date(),
            category_id=test_category.id,
            account_id=test_account.id
        )
        test_db.add(new_expense)
        await test_db.flush()
        expense_id = new_expense.id
        account_id = test_account.id
        
        # Учитываем, что расход уже создан и повлиял на баланс счёта
        test_account.balance -= expense_amount
    
    # Проверяем начальный баланс счёта
    response = test_client.get(f"/api/accounts/{account_id}")
    account_before = response.json()
    assert float(account_before["balance"]) == 2700.0
    
    # Отправляем запрос на удаление расхода
    response = test_client.delete(f"/api/expenses/{expense_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    deleted_expense = response.json()
    assert deleted_expense["description"] == "Расход для удаления"
    
    # Проверяем, что расход действительно удалён
    response = test_client.get(f"/api/expenses/{expense_id}")
    assert response.status_code == 404
    
    # Проверяем, что баланс счёта вернулся к исходному
    response = test_client.get(f"/api/accounts/{account_id}")
    account_after = response.json()
    assert float(account_after["balance"]) == 3000.0


@pytest.mark.asyncio
async def test_get_expenses_summary(test_client, test_db):
    # Создаём необходимые зависимости
    test_categories = [
        Category(name="Еда"),
        Category(name="Транспорт")
    ]
    test_account = Account(name="Общий счёт", balance=Decimal("10000.0"))
    
    async with test_db.begin():
        test_db.add_all([*test_categories, test_account])
        await test_db.flush()
        food_category_id = test_categories[0].id
        transport_category_id = test_categories[1].id
        account_id = test_account.id
        
        # Создаём несколько тестовых расходов по разным категориям
        test_expenses = [
            # Расходы на еду
            Expense(
                description="Продукты в магазине",
                amount=Decimal("500.0"),
                spent_at=datetime.now().date(),
                category_id=food_category_id,
                account_id=account_id
            ),
            Expense(
                description="Обед в кафе",
                amount=Decimal("300.0"),
                spent_at=datetime.now().date(),
                category_id=food_category_id,
                account_id=account_id
            ),
            # Расходы на транспорт
            Expense(
                description="Такси",
                amount=Decimal("200.0"),
                spent_at=datetime.now().date(),
                category_id=transport_category_id,
                account_id=account_id
            ),
            Expense(
                description="Бензин",
                amount=Decimal("400.0"),
                spent_at=datetime.now().date(),
                category_id=transport_category_id,
                account_id=account_id
            ),
        ]
        test_db.add_all(test_expenses)
    
    # Запрашиваем сводку по расходам
    current_month = datetime.now().strftime("%Y-%m")
    response = test_client.get(f"/api/expenses/summary/{current_month}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    summary = response.json()
    
    # Проверяем сводку по категориям
    summary_dict = {item["category"]: item["total"] for item in summary}
    assert "Еда" in summary_dict
    assert "Транспорт" in summary_dict
    assert float(summary_dict["Еда"]) == 800.0
    assert float(summary_dict["Транспорт"]) == 600.0
