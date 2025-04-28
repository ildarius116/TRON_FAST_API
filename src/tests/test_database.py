import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict

from src.main import app
from src.models.history import HistoryModel
from src.repositories.history import HistoryRepo
from src.services.history import HistoryService


@pytest.mark.asyncio
async def test_required_fields(test_db_session: AsyncSession, clean_db):
    """Тест обязательных полей модели"""

    test_data = HistoryModel(address="required_only")

    # добавление данных в БД
    test_db_session.add(test_data)
    await test_db_session.commit()

    # обновление тестовых данных
    await test_db_session.refresh(test_data)

    # проверка
    assert test_data.id == 1
    assert test_data.address == "required_only"
    assert test_data.bandwidth is None
    assert test_data.energy is None
    assert test_data.balance is None
    assert test_data.timestamp is not None


@pytest.mark.asyncio
async def test_simple_add_one(test_db_session: AsyncSession, clean_db, history_test_data):
    """
    Тест создания записи в БД напрямую
    """

    # добавление данных в БД
    test_db_session.add(history_test_data)
    await test_db_session.commit()
    await test_db_session.refresh(history_test_data)

    # запрос данных из БД
    result = await test_db_session.execute(select(HistoryModel))
    result = result.scalars().all()

    # проверка
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].timestamp is not None
    assert result[0].address == "full_fields_address"
    assert result[0].bandwidth == 123.45
    assert result[0].energy == 67.89
    assert result[0].balance == 987.65


@pytest.mark.asyncio
async def test_simple_add_multiple_history(test_db_session: AsyncSession, clean_db):
    """Тест создания нескольких записей"""

    test_data = [
        HistoryModel(address=f"test_address_{i}", bandwidth=i * 10, energy=i * 5, balance=i * 100)
        for i in range(1, 4)
    ]

    # добавление данных в БД
    test_db_session.add_all(test_data)
    await test_db_session.commit()

    # запрос данных из БД
    result = await test_db_session.execute(select(HistoryModel).order_by(HistoryModel.address))
    result = result.scalars().all()

    # проверка
    assert len(result) == 3
    assert result[0].address == "test_address_1"
    assert result[1].bandwidth == 20.0
    assert result[2].energy == 15.0


@pytest.mark.asyncio
async def test_history_service(clean_db, mock_account_data):
    """
    Тест создания записи в БД напрямую
    """

    # добавление данных в БД
    history_id = await HistoryService(HistoryRepo).add_history(mock_account_data)
    assert history_id is not None

    # запрос данных из БД
    result = await HistoryService(HistoryRepo).get_history_one(history_id)

    # проверка
    assert result.timestamp is not None
    assert result.address == "full_fields_address"
    assert result.balance == 1000.0
    assert result.bandwidth == 50.0
    assert result.energy == 20.0


#TODO
# разобраться с моканьтем и включить тест
@pytest.mark.asyncio
async def _test_db_save_with_real_flow(test_db_session: AsyncSession, clean_db):
    """
    Тест корректности сохранения данных в БД через API
    """

    # # создание мок-данных
    mock_account_data: Dict[str, Any] = {
        "balance": 1000.0,
        "bandwidth": {"available": 50.0},
        "energy": {"available": 20.0}
    }

    with patch("tronpy.tron.Tron.get_account", return_value=mock_account_data), \
            patch("tronpy.tron.Tron.is_address", return_value=True):
        # подмена зависимости БД
        # app.dependency_overrides[get_db_session] = lambda: test_db_session

        # имитация вызова API
        client = TestClient(app)
        response = client.post(
            url="/address/",
            json={"address": "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL"}
        )
        print(f"\n  test_db_save_with_real_flow response: {response}")
        print(f"  test_db_save_with_real_flow response.json: {response.json()}")
        assert response.status_code == 200

        test_data = HistoryModel(**response.json())

        # добавление данных в БД
        # test_db_session.add(test_data)
        # await test_db_session.commit()
        history_id = await HistoryService(HistoryRepo).add_history(response.json())
        result = await HistoryService(HistoryRepo).get_history_one(history_id)

        # query = select(HistoryModel).where(HistoryModel.address == "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL")
        # print(f"    test_db_save_with_real_flow query: {query}")
        # result = await test_db_session.execute(query)
        # print(f"    test_db_save_with_real_flow result: {result}")
        # result = result.scalars().all()
        # result = result.scalars().first()
        # result = result.scalar_one()
        print(f"\n    test_db_save_with_real_flow result: {history_id}, result: {result}")
        assert result is not None
        assert result.balance == 1000.0

    # app.dependency_overrides.clear()
