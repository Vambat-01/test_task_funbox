# Web-приложение для простого учета посещенных ccылок

## Установка зависимостей
1. Установите зависимости: `pip install -r requirements.txt`

## Запуск Web-приложения
1. Запустите [Redis](https://redis.io/): `docker run --name task_funbox --publish=6379:6379 -d redis`
1. Запустите `web-приложение`: `python server.py "0.0.0.0" 8000 "localhost" 6379 `
1. Проверьте работоспособность приложения
    - Запустите юнит тесты: `python -m unittest tests/unit_tests.py`
    - Запустите системные тесты: `python -m unittest tests/system_tests.py`
    - Тесты должны успешно пройти
