import argparse
import csv
import inspect
from pathlib import Path
import statistics
from collections import defaultdict

from tabulate import tabulate

parser = argparse.ArgumentParser(description='Скрипт читает файлы с данными и формирует отчеты')
parser.add_argument('--files', nargs='+', type=str, required=True, help='путь к файлу/файлам')
parser.add_argument('--report', '-r', type=str, help='название отчета', choices=['median_coffee'])
args = parser.parse_args()


class Data:
    def __init__(self):
        self.data = []

    def read_files(self, files: list | tuple):
        """
        Метод заполняет атрибут data данными из нескольких файлов
        :param files: список путей к файлам
        :return: None | NotImplemented если разные расширения файлов
        """
        for path in files:
            if path.endswith('.csv'):
                self.data.extend(self.read_csv(path))
            else:
                return NotImplemented

    def read_csv(self, filepath: Path) -> list:
        """
        Метод для считывания данных из csv-файла
        :param filepath: путь к файлу
        :return: список с
        """
        result = []
        with open(filepath, 'r', encoding='utf-8') as csv_file:
            for line in csv.DictReader(csv_file):
                result.append(line)
        return result

    def prepare_coffee_data(self):
        result = defaultdict(list)
        for item in self.data:
            stud = item['student']
            result[stud].append(int(item['coffee_spent']))
        return result

    """def drop_columns(self, columns: list | tuple | None = None, exclude: list | tuple | None = None):

        if not any((columns, exclude)):
            raise ValueError(f'Требуется указать 1 из параметров: {inspect.signature(self.drop_columns)}')

        for item in self.data:
            if columns:
                for column in columns:
                    item.pop(column, None)
            else:
                for key in item.copy():
                    if key not in exclude:
                        del item[key]
    """

    """def group_by(self, data: list, by: str, how: str):
        p = {}
        result = []

        if how == 'sum':
            for item in data.copy():
                by_key = item.pop(by)
                if by_key not in p:
                    p[by_key] = item
                else:
                    for key in item:
                        p[by_key][key] = int(p[by_key][key])
                        p[by_key][key] += int(item[key])
        else:
            return NotImplemented

        print(p)
    """


class ReportGenerator:
    def __init__(self, report_mode: str):
        self.report_mode = report_mode

    def generate_report(self, data: Data):
        if self.report_mode == 'median_coffee':
            stud_coffee = data.prepare_coffee_data()
            result = {k: statistics.median(v) for k, v in stud_coffee.items()}
            print(tabulate(result.items(), headers=['student', self.report_mode], tablefmt="fancy_grid"))
        else:
            print(f'значение параметра "report" = {self.report_mode} не поддерживается')


reader = Data()
reader.read_files(args.files)

report = ReportGenerator(args.report)
report.generate_report(reader)
# report.create_report(reader)
