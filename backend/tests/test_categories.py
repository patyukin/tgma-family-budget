import pytest
from httpx import AsyncClient

from app.models import Category


@pytest.mark.asyncio
async def test_create_category(test_client, test_db):
    # Подготавливаем данные для создания категории
    category_data = {
        "name": "Тестовая категория"
    }
    
    # Отправляем запрос на создание категории
    response = test_client.post("/api/categories/", json=category_data)
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    created_category = response.json()
    assert created_category["name"] == category_data["name"]
    assert "id" in created_category


@pytest.mark.asyncio
async def test_get_all_categories(test_client, test_db):
    # Создаём несколько тестовых категорий напрямую через ORM
    async with test_db.begin():
        test_categories = [
            Category(name="Продукты"),
            Category(name="Развлечения")
        ]
        test_db.add_all(test_categories)
    
    # Запрашиваем список всех категорий
    response = test_client.get("/api/categories/")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 2  # Может быть больше 2, если были и другие категории
    
    # Проверяем, что наши категории присутствуют в ответе
    category_names = [category["name"] for category in categories]
    assert "Продукты" in category_names
    assert "Развлечения" in category_names


@pytest.mark.asyncio
async def test_get_category_by_id(test_client, test_db):
    # Создаём тестовую категорию напрямую через ORM
    new_category = Category(name="Коммунальные услуги")
    
    async with test_db.begin():
        test_db.add(new_category)
        await test_db.flush()
        category_id = new_category.id
    
    # Запрашиваем категорию по ID
    response = test_client.get(f"/api/categories/{category_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    category = response.json()
    assert category["name"] == "Коммунальные услуги"


@pytest.mark.asyncio
async def test_update_category(test_client, test_db):
    # Создаём тестовую категорию напрямую через ORM
    new_category = Category(name="Старое название")
    
    async with test_db.begin():
        test_db.add(new_category)
        await test_db.flush()
        category_id = new_category.id
    
    # Данные для обновления
    update_data = {
        "name": "Обновлённое название"
    }
    
    # Отправляем запрос на обновление категории
    response = test_client.put(f"/api/categories/{category_id}", json=update_data)
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    updated_category = response.json()
    assert updated_category["name"] == update_data["name"]


@pytest.mark.asyncio
async def test_delete_category(test_client, test_db):
    # Создаём тестовую категорию напрямую через ORM
    new_category = Category(name="Категория для удаления")
    
    async with test_db.begin():
        test_db.add(new_category)
        await test_db.flush()
        category_id = new_category.id
    
    # Отправляем запрос на удаление категории
    response = test_client.delete(f"/api/categories/{category_id}")
    
    # Проверяем статус-код и данные ответа
    assert response.status_code == 200
    deleted_category = response.json()
    assert deleted_category["name"] == "Категория для удаления"
    
    # Проверяем, что категория действительно удалена
    response = test_client.get(f"/api/categories/{category_id}")
    assert response.status_code == 404
