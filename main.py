import os
import csv
import argparse
import statistics
from typing import Type
from abc import ABC, abstractmethod
from collections import defaultdict

from tabulate import tabulate


class CSVReader:
    def _validate_path(self, filepath: str):
        if not os.path.exists(filepath):
            raise ValueError(f'файл не найден: {filepath}')
        elif not self.can_read(filepath):
            raise ValueError(f'не поддерживаемый формат файла: {filepath}')

    @staticmethod
    def can_read(filepath: str) -> bool:
        return filepath.endswith('.csv')

    def read(self, filepath: str) -> list[dict]:
        self._validate_path(filepath)

        result = []
        with open(filepath, 'r', encoding='utf-8') as csv_file:
            for line in csv.DictReader(csv_file):
                result.append(line)
        return result


class ConsoleReport(ABC):
    """Асбтрактный класс для генерации отчетов"""

    def __init__(self):
        self.reader = CSVReader()

    def _read_files(self, files: list[str]) -> list[dict]:
        data = []

        for path in files:
            data.extend(self.reader.read(path))

        return data

    def generate(self, files: list[str]) -> dict:
        """
        Логика генерации и вывода отчета
        :param files: список путей к файлам
        :return: словарь преобразованных данных
        """
        data = self._read_files(files)
        data = self._aggregate(data)
        data = self._calculate(data)

        return data

    @abstractmethod
    def _aggregate(self, read_data: list[dict]) -> dict:
        """Логика аггрегирования"""
        raise NotImplementedError

    @abstractmethod
    def _calculate(self, aggregate_data: dict) -> dict:
        """Логика расчетов"""
        raise NotImplementedError

    @abstractmethod
    def render(self, generate_data: dict):
        """логика формирования отображения отчета"""
        raise NotImplementedError


class MedianCoffeeReport(ConsoleReport):
    def _aggregate(self, data: list[dict]) -> dict[str, list[float]]:
        student_coffee_agg = defaultdict(list)

        for item in data:
            if 'student' not in item or 'coffee_spent' not in item:
                continue

            student = item['student']
            num_coffee_spent = float(item['coffee_spent'])
            student_coffee_agg[student].append(num_coffee_spent)

        return student_coffee_agg

    def _calculate(self, aggregate_data: dict) -> dict[str, float]:
        median_coffe_by_stud = {k: statistics.median(v) for k, v in aggregate_data.items()}
        median_coffe_by_stud = dict(sorted(median_coffe_by_stud.items(), key=lambda item: item[1], reverse=True))
        return median_coffe_by_stud

    def render(self, generate_data: dict) -> str:
        headers = ('student', 'median_coffee')
        str_table = tabulate(generate_data.items(), headers=headers, tablefmt='fancy_grid')

        return str_table


class ReportFactory:
    def __init__(self):
        self._registry = {}

    def register(self, name: str, report_cls: Type[ConsoleReport]):
        if not issubclass(report_cls, ConsoleReport):
            raise ValueError('report_cls должен быть подтипом ConsoleReport')
        self._registry[name] = report_cls

    def create(self, name: str) -> ConsoleReport:
        if name not in self._registry:
            raise ValueError(f'неподдерживаемый отчет: {name}')
        return self._registry[name]()


class Script:
    """
    Класс-оркестратор для обработки разных видов отчетов
    """

    def __init__(self, report_factory: ReportFactory):
        self.report_factory = report_factory

        self.description = 'Скрипт читает файлы с данными и формирует отчеты'
        self.files_arg = 'files'
        self.report_arg = 'report'

    def run(self):
        try:
            cmd_args = self.get_args()
            report_mode = cmd_args.report
            files = cmd_args.files

            report = self.report_factory.create(report_mode)
            content = report.generate(files)

            print(report.render(content))

        except ValueError as err:
            print(f'ошибка: {str(err)}')

    def get_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument(f'--{self.files_arg}', nargs='+', type=str, required=True, help='путь к файлу/файлам')
        parser.add_argument(
            f'--{self.report_arg}',
            type=str,
            help='название отчета',
            required=True,
        )
        args = parser.parse_args()

        return args


def main() -> None:
    report_factory = ReportFactory()
    report_factory.register('median_coffee', MedianCoffeeReport)

    script = Script(report_factory)
    script.run()


if __name__ == '__main__':
    main()
