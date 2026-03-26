# Тестовое задание 

## О проекте
Данный репозиторий создан для выполнения тестового задания.
Проект представляет собой python-скрипт для генерации отчета.

## Структура проекта
- main.py - основной скрипт
- data - входные данные
- tests - тесты pytest

## Функционал
Функционал проекта исполнен в соответствии с требованиями 
[технического задания](docs%2F%D2%C7%20python%20junior%20%28%EC%E0%F0%F2%202026%29.%20%CE%F2%F7%E5%F2%20%EE%20%EF%EE%F2%F0%E5%E1%EB%E5%ED%E8%E8%20%EA%EE%F4%E5.docx)
. Точка входа в программу исполнена в виде функции main()

Для добавления нового отчета требуется:
1. создать класс, наследуемый от абстрактного класса ConsoleReport.
2. определить абстрактные методы с логикой 
аггрегирования(_aggregate) и расчётов (_calculate) данных
3. зарегистрировать класс отчета в ReportFactory
```
# добавить в функцию main()
report_factory.register('some_report', SomeReportClass)
```

## Пример запуска скрипта
![img.png](docs/example_launch.png)

## Запуск
1. установить зависимости
```commandline
pip install -r reqirements.txt
```
2. получить отчет
```commandline
python main.py --files data/math.csv data/physics.csv data/programming.csv --report median_coffee
```
3. тесты
```commandline
pytest
```
