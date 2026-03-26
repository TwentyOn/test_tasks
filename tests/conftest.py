import sys
import csv
import random

import pytest
from faker import Faker

from main import CSVReader, MedianCoffeeReport, Script, ReportFactory

faker = Faker()
Faker.seed(42)


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
def fake_valid_files(tmp_path, fake_valid_data) -> list[str]:
    filepaths = []
    for i in range(3):
        path = tmp_path / f'valid_csv{i + 1}.csv'
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['student', 'date', 'coffee_spent'])
            writer.writeheader()
            writer.writerows(fake_valid_data)
        filepaths.append(str(path))
    return filepaths


@pytest.fixture
def fake_empty_file(tmp_path):
    filepath = tmp_path / 'empty_csv.csv'

    with open(filepath, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['student', 'date', 'coffee_spent'])
        writer.writeheader()

    return str(filepath)


@pytest.fixture
def fake_csv_reader_cls():
    return CSVReader


@pytest.fixture
def fake_report_obj(fake_csv_reader_cls):
    return MedianCoffeeReport()


@pytest.fixture
def fake_script_obj(report_factory):
    return Script(report_factory)


@pytest.fixture
def report_factory():
    report_factory = ReportFactory()
    report_factory.register('median_coffee', MedianCoffeeReport)
    return report_factory
