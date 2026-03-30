from .base import ConsoleReport
from typing import Type


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