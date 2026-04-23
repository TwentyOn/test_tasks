from collections import defaultdict
import statistics

from tabulate import tabulate

from reports.base import ConsoleReport
from models import MedianCoffeeRecord


class ClickbaitReport(ConsoleReport):
    def _aggregate(self, data: list[MedianCoffeeRecord]) -> dict[str, list[float]]:
        student_coffee_agg = defaultdict(list)

        for record in data:
            student_coffee_agg[record.student].append(record.coffee_spent)

        return student_coffee_agg

    def _calculate(self, aggregate_data: dict) -> dict[str, float]:
        median_coffe_by_stud = {k: statistics.median(v) for k, v in aggregate_data.items()}
        median_coffe_by_stud = dict(sorted(median_coffe_by_stud.items(), key=lambda item: item[1], reverse=True))
        return median_coffe_by_stud

    def render(self, generate_data: dict) -> str:
        headers = ('student', 'median_coffee')
        str_table = tabulate(generate_data.items(), headers=headers, tablefmt='fancy_grid')

        return str_table
