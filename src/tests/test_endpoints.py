import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict

from src.database import get_db_session
from src.main import app
from src.models.history import HistoryModel


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_logs_without_pages(test_db_session: AsyncSession):
    """
    Тест корректности работы API и формат пагинированного ответа без указания пагинации
    """
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test",
                           ) as ac:
        response = await ac.get("/logs/")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 10


@pytest.mark.asyncio
async def test_get_logs_with_pages(test_db_session: AsyncSession):
    """
    Тест корректности работы API и формат пагинированного ответа с указанием пагинации
    """
    async with AsyncClient(transport=ASGITransport(app),
                           base_url="http://test",
                           ) as ac:
        response = await ac.get("/logs/?page=1&per_page=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5


@pytest.mark.asyncio
async def test_invalid_address():
    """
    Тест отправки неверного адреса
    """
    with patch("tronpy.tron.Tron.is_address", return_value=False):
        # имитация вызова API с неверным адресом
        client = TestClient(app)
        response = client.post("/address/", json={"address": "invalid"})

        assert response.status_code == 400
        assert "Invalid address" in response.json()["detail"]


@pytest.mark.asyncio
async def test_empty_page():
    """
    Тест получения пустой страницы
    """
    # имитация вызова API с неверным адресом
    client = TestClient(app)
    response = client.get("/logs/?page=99&per_page=10")
    assert len(response.json()["logs"]) == 0


@pytest.mark.asyncio
async def test_get_logs_mocked(test_db_session: AsyncSession):
    """
    Тест корректности работы API и формат пагинированного ответа с "мок" данными
    """
    # Очищаем и добавляем ТОЛЬКО тестовые данные
    await test_db_session.execute(delete(HistoryModel))
    await test_db_session.commit()

    test_log = HistoryModel(
        address="test_address",
        bandwidth=100.0,
        energy=50.0,
        balance=1000.0
    )
    test_db_session.add(test_log)
    await test_db_session.commit()

    # подмена зависимости БД
    app.dependency_overrides[get_db_session] = lambda: test_db_session

    # имитация вызова API с пагинацией
    client = TestClient(app)
    response = client.get("/logs/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 1
    assert data["logs"][0]["address"] == "test_address"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_post_address(test_db_session: AsyncSession):
    """
    Тест корректности работы API и формат данных JSON-ответов
    """
    # создание мок-данных
    mock_response: Dict[str, Any] = {
        "balance": 1000.0,
        "bandwidth": {"available": 50.0},
        "energy": {"available": 20.0}
    }

    with patch("tronpy.tron.Tron.get_account", return_value=mock_response), \
            patch("tronpy.tron.Tron.is_address", return_value=True):
        # подмена зависимости БД
        app.dependency_overrides[get_db_session] = lambda: test_db_session

        # имитация вызова API
        client = TestClient(app)
        response = client.post(
            url="/address/",
            json={"address": "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "address": "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL",
            "bandwidth": 50.0,
            "energy": 20.0,
            "balance": 1000.0
        }

    app.dependency_overrides.clear()
