from dataclasses import dataclass
import statistics


@dataclass
class MedianCoffeeRecord:
    student: str
    coffee_spent: int

    @classmethod
    def from_dict(cls, data):
        return cls(
            student=data['student'],
            coffee_spent=data['coffee_spent']
        )
