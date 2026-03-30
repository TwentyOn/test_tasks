from reports.base import ConsoleReport
from collections import defaultdict
import statistics
from tabulate import tabulate


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
