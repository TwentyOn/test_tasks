from dataclasses import dataclass


@dataclass
class BaseRecord:
    title: str
    ctr: float
    retention_rate: int
    views: int
    likes: int
    avg_watch_time: float

    def __post_init__(self):
        self.ctr = float(self.ctr)
        self.retention_rate = int(self.retention_rate)
        self.views = int(self.views)
        self.likes = int(self.likes)
        self.avg_watch_time = float(self.avg_watch_time)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class ClickbaitReportRecord:
    title: str
    ctr: float
    retention_rate: int

    @classmethod
    def from_base_record(cls, record: BaseRecord):
        return cls(
            title=record.title,
            ctr=record.ctr,
            retention_rate=record.retention_rate
        )
