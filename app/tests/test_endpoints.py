import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict
from app.database import get_db
from app.main import app
from app.models import RequestLog


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_post_address(db_session: AsyncSession):
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
        app.dependency_overrides[get_db] = lambda: db_session

        # имитация вызова API
        client = TestClient(app)
        response = client.post(
            "/address/",
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


@pytest.mark.asyncio
async def test_get_logs(db_session: AsyncSession):
    """
    Тест корректности работы API и формат пагинированного ответа
    """
    # Очищаем и добавляем ТОЛЬКО тестовые данные
    await db_session.execute(delete(RequestLog))
    await db_session.commit()

    test_log = RequestLog(
        address="test_address",
        bandwidth=100.0,
        energy=50.0,
        balance=1000.0
    )
    db_session.add(test_log)
    await db_session.commit()

    # подмена зависимости БД
    app.dependency_overrides[get_db] = lambda: db_session

    # имитация вызова API с пагинацией
    client = TestClient(app)
    response = client.get("/logs/?page=1&per_page=5")

    assert response.status_code == 200
    data = response.json()
    assert len(data["logs"]) == 1
    assert data["logs"][0]["address"] == "test_address"

    app.dependency_overrides.clear()


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
    response = client.get("/logs/?page=999&per_page=10")
    assert len(response.json()["logs"]) == 0
