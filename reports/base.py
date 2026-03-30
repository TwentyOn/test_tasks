from abc import ABC, abstractmethod
from csv_reader import CSVReader


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
