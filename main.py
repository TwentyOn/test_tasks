import argparse
import csv
import statistics
from collections import defaultdict
from abc import ABC, abstractmethod
from typing import Iterable
import os

from tabulate import tabulate


class FileReader(ABC):
    @abstractmethod
    def can_read(self, filepath: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def read(self, filepath: str) -> list[dict]:
        raise NotImplementedError


class CSVReader(FileReader):
    def can_read(self, filepath: str) -> bool:
        return filepath.endswith('.csv')

    def read(self, filepath: str) -> list[dict]:
        result = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as csv_file:
                for line in csv.DictReader(csv_file):
                    result.append(line)
            return result
        raise ValueError(f'файл не найден: {filepath}')


class ConsoleReport(ABC):
    """Асбтрактный класс для генерации отчетов"""

    @abstractmethod
    def _read(self, files: Iterable) -> list[dict]:
        """Логика чтения данных"""
        raise NotImplementedError

    @abstractmethod
    def _aggregate(self, data: Iterable) -> dict:
        """Логика аггрегирования"""
        raise NotImplementedError

    @abstractmethod
    def _calculate(self, aggregate_data: Iterable):
        """Логика расчетов"""
        raise NotImplementedError

    @abstractmethod
    def generate(self, files: list[str]):
        """
        Логика генерации и вывода отчета
        :param files: список путей к файлам
        :return:
        """
        raise NotImplementedError


class MedianCoffeeReport(ConsoleReport):
    def __init__(self, readers: set[FileReader]):
        self.readers = readers

    def _read(self, files) -> list[dict]:
        data = []

        for path in files:
            for reader in self.readers:
                if reader.can_read(path):
                    data.extend(reader.read(path))

        return data

    def _aggregate(self, data) -> dict:
        student_coffee_agg = defaultdict(list)

        for item in data:
            if 'student' not in item or 'coffee_spent' not in item:
                continue

            student = item['student']
            num_coffee_spent = float(item['coffee_spent'])
            student_coffee_agg[student].append(num_coffee_spent)

        return student_coffee_agg

    def _calculate(self, aggregate_data) -> dict:
        median_coffe_by_stud = {k: statistics.median(v) for k, v in aggregate_data.items()}
        median_coffe_by_stud = dict(sorted(median_coffe_by_stud.items(), key=lambda item: item[1], reverse=True))
        return median_coffe_by_stud

    def generate(self, files: list[str]) -> str:
        data = self._read(files)
        data = self._aggregate(data)
        data = self._calculate(data)

        headers = ('student', 'median_coffee')
        str_table = tabulate(data.items(), headers=headers, tablefmt='fancy_grid')

        return str_table


class ReadersFactory:
    _registry = {}

    @classmethod
    def register(cls, name, reader_cls: FileReader):
        cls._registry[name] = reader_cls

    @classmethod
    def create_by_files(cls, files) -> set[FileReader]:
        result = set()
        for filename in files:
            try:
                extension = filename.split('.')[-1]
                reader_cls = cls._registry[extension]
                result.add(reader_cls())
            except Exception as err:
                raise ValueError(f'неподдерживаемый формат файла: {filename}')

        return result


class ReportFactory:
    _registry = {}

    @classmethod
    def register(cls, name, report_cls):
        cls._registry[name] = report_cls

    @classmethod
    def create(cls, name, readers):
        print(name, readers)
        if name not in cls._registry:
            raise ValueError(f'Неподдерживаемый отчет: {name}')
        return cls._registry[name](readers)


class Script:
    """
    Класс-оркестратор для обработки разных видов отчетов
    """

    def run(self):
        try:
            cmd_args = self.get_args()
            report_mode = cmd_args.report
            files = cmd_args.files

            readers = ReadersFactory.create_by_files(files)
            report = ReportFactory.create(report_mode, readers)

            print(report.generate(files))

        except (ValueError, IOError) as err:
            print(f'ошибка: {str(err)}')

    @staticmethod
    def get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='Скрипт читает файлы с данными и формирует отчеты')
        parser.add_argument('--files', nargs='+', type=str, required=True, help='путь к файлу/файлам')
        parser.add_argument(
            '--report',
            type=str,
            help='название отчета',
            required=True,
        )
        args = parser.parse_args()

        return args


def main() -> None:
    readers_factory = ReadersFactory()
    readers_factory.register('csv', CSVReader)

    report_factory = ReportFactory()
    report_factory.register('median_coffee', MedianCoffeeReport)

    script = Script()
    script.run()


if __name__ == '__main__':
    main()
