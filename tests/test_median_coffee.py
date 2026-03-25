import sys
import statistics
from argparse import Namespace

import pytest



class TestScript:
    def test_get_args(self, monkeypatch, fake_script_obj):
        test_args = ['script.py', '--files', 'data1.csv', 'data2.csv', '--report', 'median_coffee']
        monkeypatch.setattr(sys, 'argv', test_args)

        assert fake_script_obj.get_args() == Namespace(files=['data1.csv', 'data2.csv'], report='median_coffee')

    def test_run_without_params(self, monkeypatch, fake_script_obj):
        with pytest.raises(SystemExit):
            fake_script_obj.run()

    def test_run_invalid_files(self, capsys, monkeypatch, fake_script_obj):
        test_args = ['script.py', '--files', 'data1.inv', 'data2.inv', '--report', 'median_coffee']
        monkeypatch.setattr(sys, 'argv', test_args)

        fake_script_obj.run()
        stream = capsys.readouterr()

        assert 'неподдерживаемый формат файла' in stream.out



class TestCsvReader:
    def test_can_read(self, fake_csv_reader_cls):
        assert fake_csv_reader_cls().can_read('test.csv')
        assert not fake_csv_reader_cls().can_read('test.txt')

    def test_read_valid_file(self, fake_csv_reader_cls, fake_valid_file, fake_valid_data):
        result = fake_csv_reader_cls().read(fake_valid_file)

        assert len(result) == len(fake_valid_data)
        assert len(result[0]) == len(fake_valid_data[0])
        assert result[5]['student'] == fake_valid_data[5]['student']
        assert result[5]['coffee_spent'] == fake_valid_data[5]['coffee_spent']

    def test_read_empty_csv(self, fake_csv_reader_cls, fake_empty_file):
        result = fake_csv_reader_cls().read(fake_empty_file)

        assert len(result) == 0
        assert result == []


class TestMedianCoffeeReport:
    def test_read(self, fake_report_obj, fake_valid_file, fake_valid_data):
        assert len(fake_report_obj._read([fake_valid_file])) == len(fake_valid_data)
        assert fake_report_obj._read([fake_valid_file])[5]['student'] == fake_valid_data[5]['student']

    def test_aggregate(self, fake_report_obj, fake_valid_data, fake_valid_file):
        unique_students = set((item['student'] for item in fake_valid_data))

        test_data = fake_report_obj._read([fake_valid_file])
        test_data = fake_report_obj._aggregate(test_data)

        assert len(test_data) == len(unique_students)

    def test_calculate_median(self, fake_report_obj, fake_valid_data, fake_valid_file):
        stud = fake_valid_data[10]['student']
        stud_data = filter(lambda item: item['student'] == stud, fake_valid_data)
        stud_data = map(lambda item: float(item['coffee_spent']), stud_data)
        median = statistics.median(stud_data)

        test_data = fake_report_obj._read([fake_valid_file])
        test_data = fake_report_obj._aggregate(test_data)
        test_data = fake_report_obj._calculate(test_data)
        test_median = test_data[stud]

        assert test_median == median

    def test_generate(self, fake_report_obj, fake_valid_file, fake_empty_file):
        report = fake_report_obj.generate([fake_valid_file])
        empty_report = fake_report_obj.generate([fake_empty_file])

        assert isinstance(report, str)
        assert isinstance(empty_report, str)
