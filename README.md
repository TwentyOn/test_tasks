# Тестовое задание 

## О проекте
Данный репозиторий создан для выполнения тестового задания.
Проект представляет собой REST-API выполненное на
языке программирования Python и Django Rest Framework в 
связке с БД PostgreSQL.

## Функционал
Функционал проекта и конечные точки API
исполнены в соответствии с требованиями
[технического задания](docs/ТЗ%20Python%20-%20API%20организационной%20структуры.docx).


## Структура проекта
- backend - серверная часть приложения
- docker-compose.yaml - файл сборки docker


Backend-часть архитектурно выполнена в соответствии со 
стандартной структурой django-приложений:
- core - пакет django-проекта
- org_strucure_api - django-приложение реализующее API. 
Специфичные модули:
  - [openapi_error_schemes.py](backend%2Forg_structure_api%2Fopenapi_error_schemes.py) -
  модуль в который вынесены стандартные
  OpenAPI-схемы ответов при ошибках запроса
- Dockerfile - инструкции для сборки docker-контейнера
- requirements.txt - файл с зависимостями

## Необходимые компоненты
- Docker
- файл окружения .env

## Требования к переменным окружения
Далее привидены переменные окружения по-умолчанию, которые 
должны быть объявлены в файле .env.
```
# django
SECRET_KEY=django-insecure-mdx3c5socx7pxuh8n%iz%yg3%mjrhd*f2k@j&fieu!=s*ga--t

# db
DB_HOST=test_db
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=45652jkl
DB_PORT=5432
DB_SCHEME_NAME=hitalent_tusk
```

Файл .env с переменными окружения следует поместить в 
директорию [backend](backend) проекта (backend/.env)

## Запуск
Проект выполнен таким образом, чтобы запускаться "из коробки"
(все миграции БД применяются автоматически). Далее приведены
команды для запуска docker-compose 
(команды использованы в среде windows CMD).

1. Клонировать репозиторий (http):

```
git clone https://github.com/TwentyOn/hitalent_test_tusk.git
```

2. Перейти в директорию проекта:

```
cd hitalent_test_tusk
```

3. Создать файл .env и скопировать в него переменные среды
в соответствии с параграфом "[требования к переменным окружения](#требования-к-переменным-окружения)"

   Чтобы создать файл можно воспользоваться командами:

    windows CMD:

   ```
   echo>backend/.env
   ```
   
    Unix/linux:
    ```
   touch backend/.env
   ```

4. Запуск docker-compose:
```
docker compose up -d
```



После запуска OpenAPI-документация доступна по адресам:
- schema:  http://127.0.0.1:8000/api/schema/
- Swagger: http://127.0.0.1:8000/api/docs/

5. Запуск тестов (опционально)

```
docker compose exec -it backend python manage.py test
```

6. Остановка docker-compose
```
docker compose stop
```
