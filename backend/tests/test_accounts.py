import pytest
from httpx import AsyncClient
from decimal import Decimal

from app.schemas import AccountCreate
from app.models import Account


@pytest.mark.asyncio
async def test_create_account(test_client, test_db):
    # Подготавливаем данные для создания счёта
    account_data = {
        "name": "Тестовый счёт",
        "balance": 1000.0
    }
    
    # Отправляем запрос на создание счёта
    response = test_client.post("/api/accounts/", json=account_data)
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    created_account = response.json()
    assert created_account["name"] == account_data["name"]
    assert float(created_account["balance"]) == account_data["balance"]
    assert "id" in created_account


@pytest.mark.asyncio
async def test_get_all_accounts(test_client, test_db):
    # Создаём несколько тестовых счетов напрямую через ORM
    async with test_db.begin():
        test_accounts = [
            Account(name="Счёт 1", balance=Decimal("500.0")),
            Account(name="Счёт 2", balance=Decimal("1500.0"))
        ]
        test_db.add_all(test_accounts)
    
    # Запрашиваем список всех счетов
    response = test_client.get("/api/accounts/")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) >= 2  # Может быть больше 2, если были и другие счета
    
    # Проверяем, что наши счета присутствуют в ответе
    account_names = [account["name"] for account in accounts]
    assert "Счёт 1" in account_names
    assert "Счёт 2" in account_names


@pytest.mark.asyncio
async def test_get_account_by_id(test_client, test_db):
    # Создаём тестовый счёт напрямую через ORM
    new_account = Account(name="Запрашиваемый счёт", balance=Decimal("777.77"))
    
    async with test_db.begin():
        test_db.add(new_account)
        await test_db.flush()
        account_id = new_account.id
    
    # Запрашиваем счёт по ID
    response = test_client.get(f"/api/accounts/{account_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    account = response.json()
    assert account["name"] == "Запрашиваемый счёт"
    assert float(account["balance"]) == 777.77


@pytest.mark.asyncio
async def test_update_account(test_client, test_db):
    # Создаём тестовый счёт напрямую через ORM
    new_account = Account(name="Старое имя счёта", balance=Decimal("100.0"))
    
    async with test_db.begin():
        test_db.add(new_account)
        await test_db.flush()
        account_id = new_account.id
    
    # Данные для обновления
    update_data = {
        "name": "Обновлённое имя счёта",
        "balance": 200.0
    }
    
    # Отправляем запрос на обновление счёта
    response = test_client.put(f"/api/accounts/{account_id}", json=update_data)
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    updated_account = response.json()
    assert updated_account["name"] == update_data["name"]
    assert float(updated_account["balance"]) == update_data["balance"]


@pytest.mark.asyncio
async def test_delete_account(test_client, test_db):
    # Создаём тестовый счёт напрямую через ORM
    new_account = Account(name="Счёт для удаления", balance=Decimal("999.99"))
    
    async with test_db.begin():
        test_db.add(new_account)
        await test_db.flush()
        account_id = new_account.id
    
    # Отправляем запрос на удаление счёта
    response = test_client.delete(f"/api/accounts/{account_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    deleted_account = response.json()
    assert deleted_account["name"] == "Счёт для удаления"
    
    # Проверяем, что счёт действительно удалён
    response = test_client.get(f"/api/accounts/{account_id}")
    assert response.status_code == 404
