from tabulate import tabulate

import dataclasses
from abc import ABC, abstractmethod
from csv_reader import CSVReader
from models import BaseRecord


class ConsoleReport(ABC):
    """Асбтрактный класс для генерации отчетов"""

    def __init__(self, cls_data: type[dataclasses.dataclass]):
        self.reader = CSVReader()
        self.cls_data = cls_data

    @abstractmethod
    def _process(self, read_data: list[BaseRecord]) -> list:
        """Логика обработки данных"""
        raise NotImplementedError

    def generate(self, files: list[str]) -> None:
        """
        Логика генерации и вывода отчета
        :param files: список путей к файлам
        :return: словарь преобразованных данных
        """
        data = self.reader.read(files)
        processed_data = self._process(data)
        self.render(processed_data)

    def render(self, generate_data: list) -> None:
        """
        Логика вывода отчета в консоль
        :param generate_data:
        :return:
        """
        print(tabulate(generate_data, headers='keys', tablefmt="grid"))
