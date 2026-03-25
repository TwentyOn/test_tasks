import csv
import random

import pytest

from main import CSVReader, MedianCoffeeReport, Script


@pytest.fixture
def fake_valid_data(faker) -> list:
    data = []
    for _ in range(10):
        student = faker.name()
        for __ in range(4):
            data.append(
                {
                    'student': student,
                    'date': faker.date(),
                    'coffee_spent': str(random.randrange(100, 700))
                }
            )
    return data


@pytest.fixture
def fake_valid_file(fake_valid_data, tmp_path) -> str:
    filepath = tmp_path / 'valid_csv.csv'

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['student', 'date', 'coffee_spent'])
        writer.writeheader()
        writer.writerows(fake_valid_data)

    return str(filepath)


@pytest.fixture
def fake_empty_file(tmp_path):
    filepath = tmp_path / 'empty_csv.csv'

    with open(filepath, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['student', 'date', 'coffee_spent'])
        writer.writeheader()

    yield str(filepath)


@pytest.fixture
def fake_csv_reader():
    reader = CSVReader()
    return reader


@pytest.fixture
def fake_report_obj(fake_csv_reader):
    return MedianCoffeeReport([fake_csv_reader])


@pytest.fixture
def fake_script_obj():
    return Script()
