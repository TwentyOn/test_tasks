import os
import csv

from models import BaseRecord


class CSVReader:
    def read(self, filepaths: list[str]) -> list[BaseRecord]:
        result = []

        for path in filepaths:
            self._validate_path(path)
            with open(path, 'r', encoding='utf-8') as csv_file:
                for line in csv.DictReader(csv_file):
                    result.append(BaseRecord.from_dict(line))

        return result

    def _validate_path(self, filepath: str):
        if not os.path.exists(filepath):
            raise ValueError(f'файл не найден: {filepath}')
        elif not self.can_read(filepath):
            raise ValueError(f'не поддерживаемый формат файла: {filepath}')

    @staticmethod
    def can_read(filepath: str) -> bool:
        if isinstance(filepath, str):
            return filepath.endswith('.csv')
        return False
