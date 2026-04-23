import random
import sys
import statistics
from typing import Iterable

import pytest

from reports.base import ConsoleReport


class TestGetArgs:
    def test_get_args(self):
        pass

class TestCsvReader:
    def test_can_read(self, fake_csv_reader_cls):
        assert fake_csv_reader_cls().can_read('test.csv')
        assert not fake_csv_reader_cls().can_read('test.txt')

    def test_read(self, fake_csv_reader_cls, fake_valid_files, fake_valid_data):
        result = fake_csv_reader_cls().read(fake_valid_files[0])

        magic_index = random.randint(0, len(result) - 1)

        assert len(result) == len(fake_valid_data)
        assert len(result[magic_index]) == len(fake_valid_data[magic_index])
        assert result[magic_index]['student'] == fake_valid_data[magic_index]['student']
        assert result[magic_index]['coffee_spent'] == fake_valid_data[magic_index]['coffee_spent']

    def test_read_empty_csv(self, fake_csv_reader_cls, fake_empty_file):
        result = fake_csv_reader_cls().read(fake_empty_file)

        assert len(result) == 0
        assert result == []


class TestMedianCoffeeReport:
    def test_read_files(self, fake_report_obj, fake_valid_files, fake_valid_data):
        assert len(fake_report_obj._read_files(fake_valid_files)) == len(fake_valid_data) * 3
        assert fake_report_obj._read_files(fake_valid_files)[5]['student'] == fake_valid_data[5]['student']

    def test_aggregate(self, fake_report_obj, fake_valid_data, fake_valid_files):
        unique_students = set((item['student'] for item in fake_valid_data))

        test_data = fake_report_obj._read_files(fake_valid_files)
        test_data = fake_report_obj._aggregate(test_data)

        assert len(test_data) == len(unique_students)
        for student, spent in test_data.items():
            assert isinstance(student, str)
            assert isinstance(spent, list)
            assert all(isinstance(s, float) for s in spent)

    def test_calculate_median(self, fake_report_obj, fake_valid_data, fake_valid_files):
        stud = fake_valid_data[10]['student']
        stud_data = filter(lambda item: item['student'] == stud, fake_valid_data)
        stud_data = map(lambda item: float(item['coffee_spent']), stud_data)
        expected_median = statistics.median(stud_data)

        test_data = fake_report_obj._read_files(fake_valid_files)
        test_data = fake_report_obj._aggregate(test_data)
        test_data = fake_report_obj._calculate(test_data)
        test_median = test_data[stud]

        assert test_median == expected_median

    def test_generate(self, fake_report_obj, fake_valid_files, fake_empty_file):
        report = fake_report_obj.generate(fake_valid_files)
        empty_report = fake_report_obj.generate([fake_empty_file])

        assert isinstance(report, dict)
        assert isinstance(empty_report, dict)

    def test_render(self, fake_report_obj, fake_valid_files, fake_valid_data):
        report = fake_report_obj.generate(fake_valid_files)
        report = fake_report_obj.render(report)

        test_stud = fake_valid_data[0]['student']

        assert isinstance(report, str)
        assert test_stud in report
