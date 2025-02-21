import csv
import json
from abc import ABC, abstractmethod
from enum import Enum
from io import StringIO
from typing import Dict, Union


class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PLAIN = "plain"


class FormatStrategy(ABC):
    @abstractmethod
    def format(self, raw_result: str) -> Union[Dict, list]:
        pass

    @staticmethod
    def is_format(content: str) -> bool:
        """Metodo per verificare se il contenuto corrisponde al formato."""
        return False


class JSONFormatStrategy(FormatStrategy):
    def format(self, raw_result: str) -> Union[Dict, list]:
        return json.loads(raw_result)

    @staticmethod
    def is_format(content: str) -> bool:
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False


class CSVFormatStrategy(FormatStrategy):
    def format(self, raw_result: str) -> list:
        csv_file = StringIO(raw_result)
        reader = csv.DictReader(csv_file)
        return list(reader)

    @staticmethod
    def is_format(content: str) -> bool:
        try:
            csv_file = StringIO(content)
            reader = csv.reader(csv_file)
            rows = list(reader)
            return len(rows) > 1 and len(rows[0]) > 1
        except csv.Error:
            return False


class PlainTextFormatStrategy(FormatStrategy):
    def format(self, raw_result: str) -> Dict:
        return {"content": raw_result}


class FormatStrategyFactory:
    strategies = [
        JSONFormatStrategy,
        CSVFormatStrategy,
        PlainTextFormatStrategy,
    ]

    @classmethod
    def get_strategy(cls, raw_result: str) -> FormatStrategy:
        for strategy in cls.strategies:
            if strategy.is_format(raw_result):
                return strategy()
        return PlainTextFormatStrategy()


class StringToolFormatter:
    @staticmethod
    def from_str_to_dict(raw_result: str):
        strategy = FormatStrategyFactory.get_strategy(raw_result)
        return strategy.format(raw_result)
