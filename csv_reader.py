import os
import csv

from models import MedianCoffeeRecord


class CSVReader:
    def _validate_path(self, filepath: str):
        if not os.path.exists(filepath):
            raise ValueError(f'файл не найден: {filepath}')
        elif not self.can_read(filepath):
            raise ValueError(f'не поддерживаемый формат файла: {filepath}')

    @staticmethod
    def can_read(filepath: str) -> bool:
        return filepath.endswith('.csv')

    def read(self, filepath: str) -> list[MedianCoffeeRecord]:
        self._validate_path(filepath)

        result = []
        with open(filepath, 'r', encoding='utf-8') as csv_file:
            for line in csv.DictReader(csv_file):
                result.append(MedianCoffeeRecord.from_dict(line))
        return result
