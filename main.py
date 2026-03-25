import argparse
import csv
import statistics
from collections import defaultdict
from abc import ABC, abstractmethod

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
        with open(filepath, 'r', encoding='utf-8') as csv_file:
            for line in csv.DictReader(csv_file):
                result.append(line)
        return result


class ConsoleReport(ABC):
    """Асбтрактный класс для генерации отчетов"""

    @abstractmethod
    def _read(self, files) -> list[dict]:
        """Логика чтения данных"""
        raise NotImplementedError

    @abstractmethod
    def _aggregate(self, data) -> dict:
        """Логика аггрегирования"""
        raise NotImplementedError

    @abstractmethod
    def _calculate(self, aggregate_data):
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
        pass

    def _aggregate(self, data) -> dict:
        pass

    def _calculate(self, aggregate_data):
        pass

    def generate(self, files: list[str]) -> str:
        data = []

        for path in files:
            for reader in self.readers:
                if reader.can_read(path):
                    data.extend(reader.read(path))

        student_coffee_agg = defaultdict(list)

        for item in data:
            if 'student' not in item or 'coffee_spent' not in item:
                continue

            student = item['student']
            num_coffee_spent = float(item['coffee_spent'])
            student_coffee_agg[student].append(num_coffee_spent)

        str_table = {k: statistics.median(v) for k, v in student_coffee_agg.items()}
        str_table = dict(sorted(str_table.items(), key=lambda item: item[1], reverse=True))

        headers = ('student', 'median_coffee')
        str_table = tabulate(str_table.items(), headers=headers, tablefmt='fancy_grid')
        return str_table


class ReadersFactory:
    _registry = {}

    @classmethod
    def register(cls, name, reader_cls: FileReader):
        cls._registry[name] = reader_cls

    @classmethod
    def create_by_files(cls, files) -> list[FileReader]:
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

    def __init__(self, files: list, report_mode: str):
        self.files = files
        self.report_mode = report_mode

    def run(self):
        try:
            readers = ReadersFactory.create_by_files(self.files)
            report = ReportFactory.create(self.report_mode, readers)

            print(report.generate(self.files))

        except (ValueError, IOError) as err:
            print(f'ошибка: {str(err)}')


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

    cmd_args = get_args()
    report_mode = cmd_args.report
    files = cmd_args.files

    script = Script(files, report_mode)
    script.run()


if __name__ == '__main__':
    main()
