# Интернет-магазин

Интернет-магазин, разработанный на Django по паттерну MVC. Продавцы могут управлять товарами, а клиенты — создавать и оплачивать заказы.
Проект реализован в монолитной архитектуре


## Как запустить проект?

1. Создайте папку env и заполните файлы .db.env и .online_shop.env:
```mkdir env && > env/.db.env && > env/.online_shop.env```

#### Пример содержания файлов:

*.online_shop.env*
```
# APP
SECRET_KEY = ...
DEBUG = 1
LOGGING_LEVEL = DEBUG

# DB
DB_NAME = db
DB_USER = user
DB_PASSWORD = 12345678
DB_HOST = db
DB_POST = 5432
```

*.db.env*
```
# POSTGRES
POSTGRES_DB=optimization_app
POSTGRES_USER=optimization_app
POSTGRES_PASSWORD=12345678
```

2. Создайте папку для логов и пустой файл:
```mkdir src/logs && > src/logs/general.log ```

## Запустить проект в режиме разработки

```docker compose up --build```

## Запустить проект на продакшене

```docker compose -f docker-compose.prod.yml up --build```
