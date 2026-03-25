import csv
import random

import pytest

from main import CSVReader, MedianCoffeeReport


@pytest.fixture
def valid_csv(tmp_path, faker) -> tuple[list]:
    filepath = tmp_path / 'valid_csv.csv'
    fake_data = [
        {'student': faker.name(),
         'date': faker.date(),
         'coffee_spent': str(random.randrange(100, 700))
         }
        for _ in range(10)
    ]

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['student', 'date', 'coffee_spent'])
        writer.writeheader()
        writer.writerows(fake_data)

    yield [str(filepath)], fake_data


@pytest.fixture
def empty_csv(tmp_path):
    filepath = tmp_path / 'empty_csv.csv'

    with open(filepath, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['student', 'date', 'coffee_spent'])
        writer.writeheader()

    yield [str(filepath)]


@pytest.fixture
def fake_csv_reader():
    reader = CSVReader()
    return reader

