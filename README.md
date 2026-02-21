# Тестовое задание 

## О проекте
Данный репозиторий создан для выполнения тестового задания.
Проект представляет собой REST-API выполненное на
языке программирования Python и Django Rest Framework в 
связке с БД PostgreSQL.

## Функционал
Функционал проекта исполнен в соответствии с требованиями
технического задания

## Структура проекта
- backend - серверная часть приложения
- initial.sql - sql скрипт для создания схемы БД (требуется 
для запуска "из коробки")
- docker-compose.yaml - файл сборки docker


Backend-часть архитектурно выполнена в соответствии со 
стандартной структурой django-приложений:
- core - пакет django-проекта
- org_strucure_api - django-приложение реализующее API. 
Специфичные модули:
  - [openapi_error_schemes.py](backend%2Forg_structure_api%2Fopenapi_error_schemes.py) -
  модуль в который вынесены стандартные
  OPENAPI-схемы ответов при ошибках запроса
- Dockerfile - инструкции для сборки docker-контейнера
- requirements.txt - файл с зависимостями

## Необходимые компоненты
- Docker
- файл окружения .env

## Требования к переменным окружения
Далее привидены необходимые переменные окружения, которые 
должны быть объявлены в файле .env.
```
# django
SECRET_KEY=django-insecure-mdx3c5socx7pxuh8n%iz%yg3%mjrhd*f2k@j&fieu!=s*ga--t

# db
DB_HOST=test_db
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=643941
DB_PORT=5432
DB_SCHEME_NAME=hitalent_tusk
```

Файл .env с переменными окружения следует поместить в 
директорию [backend](backend) проекта

## Запуск
(Команды использованы в среде windows power shell)

Клонировать репозиторий:

```
git clone https://github.com/TwentyOn/hitalent_test_tusk.git
```

Перейти в директорию проекта:

```
cd hitalent_test_tusk
```

Запустить docker-compose:
```
docker compose up
```