import sys
from argparse import Namespace

import pytest
from tabulate import tabulate

from main import get_args, CSVReader, MedianCoffeeReport


def test_get_args(monkeypatch):
    test_args = ['script.py', '--files', 'data1.csv', 'data2.csv', '--report', 'median_coffee']
    monkeypatch.setattr(sys, 'argv', test_args)

    assert get_args() == Namespace(files=['data1.csv', 'data2.csv'], report='median_coffee')


class TestCsvReader:
    def test_can_read(self, fake_csv_reader):
        assert fake_csv_reader.can_read('test.csv') == True
        assert fake_csv_reader.can_read('test.txt') == False

    def test_read_valid_csv(self, fake_csv_reader, valid_csv):
        fake_filepath = valid_csv[0]
        fake_data = valid_csv[1]

        result = fake_csv_reader.read(fake_filepath[0])

        assert len(result) == len(fake_data)
        assert len(result[0]) == len(fake_data[0])
        assert result[5]['student'] == fake_data[5]['student']
        assert result[5]['coffee_spent'] == fake_data[5]['coffee_spent']

    def test_read_empty_csv(self, fake_csv_reader, empty_csv):
        fake_filepath = empty_csv

        result = fake_csv_reader.read(fake_filepath[0])

        assert len(result) == 0
        assert result == []

class TestReportGenerator:
    def 
