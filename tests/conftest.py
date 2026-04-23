import os
import sys
import csv
import random

import pytest
from faker import Faker

from main import get_args
from csv_reader import CSVReader
from reports.reports import ClickbaitReport

Faker.seed(42)


@pytest.fixture
def fake_valid_data(faker) -> list:
    data = []
    for _ in range(10):
        data.append(
            {
                'title': faker.company(),
                'ctr': str(random.randrange(0, 100)),
                'retention_rate': str(random.randrange(0, 100)),
                'views': str(random.randrange(1000, 200000)),
                'likes': str(random.randrange(1000, 50000)),
                'avg_watch_time': str(random.uniform(1, 10))
            }
        )
    return data


@pytest.fixture
def fake_valid_files(tmp_path, fake_valid_data) -> list[str]:
    filepaths = []

    for i in range(3):
        path = tmp_path / f'valid_csv{i + 1}.csv'
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=['title', 'ctr', 'retention_rate', 'views', 'likes', 'avg_watch_time'])
            writer.writeheader()
            writer.writerows(fake_valid_data)
        filepaths.append(str(path))

    return filepaths


@pytest.fixture
def fake_invalid_name_file(tmp_path):
    filepath = tmp_path / 'invalid_name.txt'

    with open(filepath, 'w') as f:
        pass

    return [str(filepath)]


@pytest.fixture
def fake_not_exist_file():
    return os.path.join('not', 'exist', 'path')


@pytest.fixture(scope='class')
def fake_csv_reader():
    return CSVReader()


@pytest.fixture(scope='class')
def fake_clickbait_report():
    return ClickbaitReport()
