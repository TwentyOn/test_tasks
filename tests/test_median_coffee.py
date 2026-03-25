import sys
from argparse import Namespace

import pytest
from tabulate import tabulate

from main import Script


class TestScript:
    def test_get_args(self, monkeypatch, fake_script_obj):
        test_args = ['script.py', '--files', 'data1.csv', 'data2.csv', '--report', 'median_coffee']
        monkeypatch.setattr(sys, 'argv', test_args)

        assert fake_script_obj.get_args() == Namespace(files=['data1.csv', 'data2.csv'], report='median_coffee')


class TestCsvReader:
    def test_can_read(self, fake_csv_reader):
        assert fake_csv_reader.can_read('test.csv') == True
        assert fake_csv_reader.can_read('test.txt') == False

    def test_read_valid_csv(self, fake_csv_reader, fake_valid_csv, fake_valid_data):
        result = fake_csv_reader.read(fake_valid_csv)

        assert len(result) == len(fake_valid_data)
        assert len(result[0]) == len(fake_valid_data[0])
        assert result[5]['student'] == fake_valid_data[5]['student']
        assert result[5]['coffee_spent'] == fake_valid_data[5]['coffee_spent']

    def test_read_empty_csv(self, fake_csv_reader, fake_empty_csv):
        files = fake_empty_csv
        result = fake_csv_reader.read(files)

        assert len(result) == 0
        assert result == []



