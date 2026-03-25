import sys
import csv
import random

import pytest

from main import CSVReader, MedianCoffeeReport, Script, ReadersFactory, ReportFactory


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
def fake_valid_files(fake_valid_data, tmp_path) -> list[str]:
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
def fake_invalid_file(tmp_path):
    filepath = tmp_path / 'invalid.file'

    with open(filepath, 'w') as f:
        pass

    return str(filepath)


@pytest.fixture
def fake_csv_reader_cls():
    return CSVReader


@pytest.fixture
def fake_report_obj(fake_csv_reader_cls):
    return MedianCoffeeReport([fake_csv_reader_cls()])


@pytest.fixture
def fake_script_obj():
    return Script()


@pytest.fixture
def valid_cmd_args(tmp_path, monkeypatch):
    files = [str(tmp_path / f'valid_csv{i}.csv') for i in range(1,4)]
    test_args = ['script.py', '--files', *files, '--report', 'median_coffee']
    monkeypatch.setattr(sys, 'argv', test_args)
    return test_args


@pytest.fixture
def initial_fake_median_factories():
    reader_factory = ReadersFactory()
    reader_factory.register('csv', CSVReader)

    report_factory = ReportFactory()
    report_factory.register('median_coffee', MedianCoffeeReport)

    yield

    reader_factory._registry.clear()
    report_factory._registry.clear()
