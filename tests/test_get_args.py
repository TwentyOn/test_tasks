import sys

import pytest

from main import get_args


class TestGetArgs:
    """
    Тесты извлечения аргументов CLI
    """

    @pytest.mark.parametrize('files, report, error', [
        (['file1.csv', 'file2.csv'], 'clickbait', False),
        (['somefile.csv', 'otherfile.csv'], 'clickbait', False),
        (['file1.csv', 'file2.csv'], 'somereport', True),
    ])
    def test_get_args(self, monkeypatch, files, report, error):
        monkeypatch.setattr(sys, 'argv', ['main.py', '--report', report, '--files', *files])
        if error:
            with pytest.raises(SystemExit):
                get_args()
        else:
            args = get_args()
            assert args.report == report
            assert args.files == files
