import argparse
import logging

from reports.median_coffee import MedianCoffeeReport
from reports.factory import ReportFactory


logging.basicConfig(level=logging.INFO, format='[{asctime}] #{levelname:4} {name}:{lineno} - {message}', style='{')
logger = logging.getLogger(__name__)

ALLOWED_REPORTS = ['median_coffee']


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
            logger.error(err)

    def get_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=self.description)

        parser.add_argument(
            f'--{self.files_arg}',
            nargs='+',
            type=str,
            required=True,
            help='путь к файлу/файлам'
        )

        parser.add_argument(
            f'--{self.report_arg}',
            type=str,
            help='название отчета',
            required=True,
            choices=ALLOWED_REPORTS
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
