import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict

from src.database import get_db
from src.main import app
from src.models.history import HistoryModel


@pytest.mark.asyncio
async def test_db_save_with_real_flow(db_session: AsyncSession):
    """
    Тест корректности сохранения данных в БД через API
    """
    # подготовка (очистка) БД
    await db_session.execute(delete(HistoryModel))
    await db_session.commit()

    # создание мок-данных
    mock_account_data: Dict[str, Any] = {
        "balance": 1000.0,
        "bandwidth": {"available": 50.0},
        "energy": {"available": 20.0}
    }

    with patch("tronpy.tron.Tron.get_account", return_value=mock_account_data), \
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
        result = await db_session.execute(select(HistoryModel).where(
            HistoryModel.address == "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL"))
        log = result.scalars().first()
        assert log is not None
        assert log.balance == 1000.0

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_log_entry(db_session: AsyncSession):
    """
    Тест создания записи в БД напрямую
    """
    # подготовка (очистка) БД
    await db_session.execute(delete(HistoryModel))
    await db_session.commit()

    test_log = HistoryModel(
        address="test_address_1",
        bandwidth=100.0,
        energy=50.0,
        balance=1000.0
    )

    # добавление данных в БД
    db_session.add(test_log)
    await db_session.commit()

    # запрос данных из БД
    result = await db_session.execute(select(HistoryModel))
    logs = result.scalars().all()

    assert len(logs) == 1
    assert logs[0].address == "test_address_1"
    assert logs[0].balance == 1000.0


@pytest.mark.asyncio
async def test_multiple_log_entries(db_session: AsyncSession):
    """Тест создания нескольких записей"""
    # подготовка (очистка) БД
    await db_session.execute(delete(HistoryModel))
    await db_session.commit()

    logs = [
        HistoryModel(address=f"test_address_{i}", bandwidth=i * 10, energy=i * 5, balance=i * 100)
        for i in range(1, 4)
    ]

    # добавление данных в БД
    db_session.add_all(logs)
    await db_session.commit()

    # запрос данных из БД
    result = await db_session.execute(select(HistoryModel).order_by(HistoryModel.address))
    saved_logs = result.scalars().all()

    assert len(saved_logs) == 3
    assert saved_logs[0].address == "test_address_1"
    assert saved_logs[1].bandwidth == 20.0
    assert saved_logs[2].energy == 15.0


@pytest.mark.asyncio
async def test_log_entry_fields(db_session: AsyncSession):
    """Тест корректности заполнения полей"""
    # подготовка (очистка) БД
    await db_session.execute(delete(HistoryModel))
    await db_session.commit()

    test_log = HistoryModel(
        address="full_fields_address",
        bandwidth=123.45,
        energy=67.89,
        balance=987.65
    )

    # добавление данных в БД
    db_session.add(test_log)
    await db_session.commit()
    await db_session.refresh(test_log)

    # проверка
    assert test_log.id is not None
    assert test_log.timestamp is not None
    assert test_log.address == "full_fields_address"
    assert pytest.approx(test_log.bandwidth) == 123.45
    assert pytest.approx(test_log.energy) == 67.89
    assert pytest.approx(test_log.balance) == 987.65


@pytest.mark.asyncio
async def test_required_fields(db_session: AsyncSession):
    """Тест обязательных полей модели"""
    # подготовка (очистка) БД
    await db_session.execute(delete(HistoryModel))
    await db_session.commit()

    test_log = HistoryModel(address="required_only")

    # добавление данных в БД
    db_session.add(test_log)
    await db_session.commit()
    await db_session.refresh(test_log)

    # проверка
    assert test_log.address == "required_only"
    assert test_log.bandwidth is None
    assert test_log.energy is None
    assert test_log.balance is None
    assert test_log.timestamp is not None
