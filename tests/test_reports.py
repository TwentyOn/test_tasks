import random
import sys

import pytest

from main import get_args
from models import BaseRecord, ClickbaitReportRecord


class TestGetArgs:
    """
    Тесты извлечения аргументов CLI
    """

    @pytest.mark.parametrize('files, report, error', [
        (['file1.csv', 'file2.csv'], 'clickbait', False),
        (['somefile.csv', 'otherfile.csv'], 'clickbait', False),
        (['file1.csv', 'file2.csv'], 'somereport', True),
    ])
    def test_get_args(self, files, report, error):
        sys.argv = ['main.py', '--report', report, '--files', *files]
        if error:
            with pytest.raises(SystemExit):
                get_args()
        else:
            args = get_args()
            assert args.report == report
            assert args.files == files


class TestCsvReader:
    """
    Тесты чтения данных из файлов
    """

    @pytest.mark.parametrize('filename, ans', [
        ('test.csv', True),
        ('test.txt', False),
        ('sometext', False),
        (1234, False)
    ])
    def test_can_read(self, fake_csv_reader, filename, ans):
        assert fake_csv_reader.can_read(filename) == ans

    @pytest.mark.parametrize('files, error', [
        ('fake_valid_files', False),
        ('fake_invalid_name_file', True),
        ('fake_not_exist_file', True)
    ])
    def test_read(self, request, fake_csv_reader, fake_valid_data, files, error):
        paths = request.getfixturevalue(files)
        if error:
            with pytest.raises(ValueError):
                fake_csv_reader.read(paths)
        else:
            data = fake_csv_reader.read(paths)
            length = len(data)

            assert length == len(fake_valid_data) * 3  # 3 файла
            assert isinstance(data[0], BaseRecord)
            assert data[0].title == fake_valid_data[0]['title']

            assert isinstance(data[0].ctr, float)
            assert isinstance(data[0].avg_watch_time, float)
            assert isinstance(data[0].views, int)
            assert isinstance(data[0].likes, int)
            assert isinstance(data[0].retention_rate, int)


class TestClickbaitReport:
    def test_generate(self, fake_clickbait_report, fake_valid_files):
        generate_data = fake_clickbait_report.generate(fake_valid_files)

        assert isinstance(generate_data, list)
        assert isinstance(generate_data[0], ClickbaitReportRecord)
        assert generate_data[0].ctr > generate_data[-1].ctr
        assert min([d.ctr for d in generate_data]) > 15.0
        assert max([d.retention_rate for d in generate_data]) < 40

    def test_render(self, capsys, fake_clickbait_report, fake_valid_files, fake_valid_data):
        generate_data = fake_clickbait_report.generate(fake_valid_files)
        fake_clickbait_report.render(generate_data)

        stream = capsys.readouterr()
        test_title = generate_data[0].title

        assert test_title in stream.out
