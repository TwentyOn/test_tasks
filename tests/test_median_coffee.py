import sys
import statistics
from argparse import Namespace
from typing import Iterable

import pytest

from main import ReadersFactory, ReportFactory, ConsoleReport, FileReader


class TestScript:
    def test_get_args(self, tmp_path, monkeypatch, fake_script_obj):
        files = [str(tmp_path / f'valid_csv{i}.csv') for i in range(1, 4)]
        cmd_args = ['script.py', '--files', *files, '--report', 'median_coffee']
        monkeypatch.setattr(sys, 'argv', cmd_args)

        test_args = fake_script_obj.get_args()
        assert all((test_file in cmd_args for test_file in test_args.files))
        assert test_args.report in cmd_args

    def test_run_without_params(self, fake_script_obj):
        with pytest.raises(SystemExit):
            fake_script_obj.run()

    def test_run_with_params(self, capsys, fake_valid_files, fake_script_obj,
                             initial_fake_median_factories):
        fake_script_obj.run()

        stream = capsys.readouterr()
        assert 'student' and 'median_coffee' in stream.out

    def test_run_invalid_files(self, capsys, monkeypatch, fake_script_obj):
        test_args = ['script.py', '--files', 'data1.inv', 'data2.inv', '--report', 'median_coffee']
        monkeypatch.setattr(sys, 'argv', test_args)

        fake_script_obj.run()
        stream = capsys.readouterr()

        assert 'неподдерживаемый формат файлов' in stream.out


class TestCsvReader:
    def test_can_read(self, fake_csv_reader_cls):
        assert fake_csv_reader_cls().can_read('test.csv')
        assert not fake_csv_reader_cls().can_read('test.txt')

    def test_read(self, fake_csv_reader_cls, fake_valid_files, fake_valid_data):
        result = fake_csv_reader_cls().read(fake_valid_files[0])

        assert len(result) == len(fake_valid_data)
        assert len(result[0]) == len(fake_valid_data[0])
        assert result[5]['student'] == fake_valid_data[5]['student']
        assert result[5]['coffee_spent'] == fake_valid_data[5]['coffee_spent']

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

    def test_calculate_median(self, fake_report_obj, fake_valid_data, fake_valid_files):
        stud = fake_valid_data[10]['student']
        stud_data = filter(lambda item: item['student'] == stud, fake_valid_data)
        stud_data = map(lambda item: float(item['coffee_spent']), stud_data)
        median = statistics.median(stud_data)

        test_data = fake_report_obj._read_files(fake_valid_files)
        test_data = fake_report_obj._aggregate(test_data)
        test_data = fake_report_obj._calculate(test_data)
        test_median = test_data[stud]

        assert test_median == median

    def test_generate(self, fake_report_obj, fake_valid_files, fake_empty_file):
        report = fake_report_obj.generate(fake_valid_files)
        empty_report = fake_report_obj.generate([fake_empty_file])

        assert isinstance(report, str)
        assert isinstance(empty_report, str)


class TestFactories:
    def test_report_factory(self):
        factory = ReportFactory()

        class TestReportClass(ConsoleReport):
            def __init__(self, reader):
                pass

            def _read_files(self, files: Iterable) -> list[dict]:
                pass

            def _aggregate(self, data: Iterable) -> dict:
                pass

            def _calculate(self, aggregate_data: Iterable):
                pass

            def generate(self, files: list[str]):
                pass

        factory.register('sum_coffee', TestReportClass)
        report = factory.create('sum_coffee', FileReader)
        assert 'sum_coffee' in factory._registry
        assert isinstance(report, TestReportClass)

    def test_reader_factory(self):
        factory = ReadersFactory()

        class TestReaderClass(FileReader):
            def read(self, filepath: str) -> list[dict]:
                pass

            def can_read(self, filepath: str) -> bool:
                pass

        factory.register('csv', TestReaderClass)
        readers = factory.create_by_files(['data1.csv', 'data2.csv'])

        assert 'csv' in factory._registry
        assert len(readers) == 1
        assert isinstance(readers.pop(), TestReaderClass)
