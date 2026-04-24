import pytest
from models import BaseRecord


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
