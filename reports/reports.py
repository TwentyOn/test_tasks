from reports.base import ConsoleReport
from models import ClickbaitReportRecord, BaseRecord


class ClickbaitReport(ConsoleReport):
    def _process(self, read_data: list[BaseRecord]) -> list[ClickbaitReportRecord]:
        filtered_data = filter(lambda item: item.ctr > 15.0 and item.retention_rate < 40, read_data)
        filtered_data = [ClickbaitReportRecord.from_base_record(r) for r in filtered_data]
        sorted_data = sorted(filtered_data, key=lambda item: item.ctr, reverse=True)
        return sorted_data


# регистрировать новые виды отчетов здесь
REPORTS: dict[str, type[ConsoleReport]] = {
    'clickbait': ClickbaitReport
}
