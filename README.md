# Микросервис на фреймворке Fast API

_Техническое задание:_
```text
Написать микросервис, который будет выводить информацию о кошельке по адресу в сети Трон (его bandwidth, energy, и баланс trx). Эндпоинт должен принимать входные данные - адрес. 
Каждый запрос писать в базу данных, с полями о том какой кошелек запрашивался. 
У сервиса 2 эндпоинта:
- POST для запроса по адресу;
- GET для получения списка последних записей из БД, включая пагинацию.
Написать юнит/интеграционные тесты:
- интеграционный на эндпоинт;
- юнит на запись в бд.
Примечания: использовать FastAPI, аннотацию(typing), SQLAlchemy ORM, для удобства по взаимодействию с троном можно использовать tronpy, для тестов Pytest.
```

__Доступные адреса (эндпоинты) и функции:__

* `/address/` - адрес отправки запроса информации в сеть Торн
* `/logs/` - адрес просмотра списка последних записей из БД
* `/logs/?page=1&per_page=5` - адрес просмотра списка последних записей из БД с указанием пагинации


## Примеры:

* ### _Отправка запроса информации:_
* ![adress.JPG](README%2Fadress.JPG)
* ### _Просмотр списка последних записей из БД:_
* ![logs_without_pagination.JPG](README%2Flogs_without_pagination.JPG)
* ![logs_with_pagination.JPG](README%2Flogs_with_pagination.JPG)

### Порядок запуска
* Клонировать: `git clone https://github.com/ildarius116/TRON_FAST_API.git`
* Установить зависимости: `pip install -r requirements.txt`
* Запустить сервис: `uvicorn app.main:app --reload`

### _Примечания:_
1. Если необходимо добавить `.env`-файл, в нем следует указать следующие данные:
```yaml
# Database Settings
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Tron Network Settings
TRON_NETWORK = "shasta"

# DEBUG Settings
DEBUG = True
```
2. Если необходимо запустить сервис на определенном хосте и порту, то указать это в строке запуска:
`uvicorn app.main:app --host $API_HOST --port $API_PORT --reload` (н-р: `uvicorn app.main:app --host 192.168.1.100 --port 8800 --reload`)
