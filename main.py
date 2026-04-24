import argparse
import logging

from reports.reports import REPORTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    """
    Получение агрументов CLI
    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        f'--files',
        nargs='+',
        type=str,
        required=True,
        help='путь к файлу/файлам'
    )

    parser.add_argument(
        f'--report',
        type=str,
        help='название отчета',
        required=True,
        choices=REPORTS.keys()
    )
    args = parser.parse_args()

    return args


def main() -> None:
    args = get_args()
    report = REPORTS.get(args.report)()
    try:
        prepare_data = report.generate(args.files)
        report.render(prepare_data)
    except Exception as err:
        logger.error(f'Ошибка генерации отчета - {err}')


if __name__ == '__main__':
    main()
