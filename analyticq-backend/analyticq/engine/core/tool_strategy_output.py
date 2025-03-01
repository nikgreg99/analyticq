import csv
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from io import StringIO
from typing import Any, Dict, List, Optional, Union


class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    SARIF = "sarif"
    PLAIN = "plain"


class FormatStrategy(ABC):
    @abstractmethod
    def format(self, raw_result: str) -> Union[Dict, list]:
        pass

    @staticmethod
    def is_format(content: str) -> bool:
        return False


class JSONFormatStrategy(FormatStrategy):
    def format(self, raw_result: str) -> Union[Dict, list]:
        return json.loads(raw_result)

    @staticmethod
    def is_format(content: str) -> bool:
        """
        Check if a string content is a valid JSON format.

        Args:
            content (str): The string to check for JSON format validity.

        Returns:
            bool: True if the content is valid JSON format, False otherwise.

        Example:
            >>> is_format('{"name": "John", "age": 30}')
            True
            >>> is_format('Invalid JSON')
            False
        """
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
        """
        Check if the given content is in a valid CSV format.

        This function attempts to parse the input string as a CSV file and determines if it has
        a valid format by checking if it contains at least one row and one column.

        Args:
            content (str): The string content to be checked for CSV format.

        Returns:
            bool: True if the content is in valid CSV format with at least one row and one column,
                  False otherwise or if parsing fails.
        """
        try:
            csv_file = StringIO(content)
            reader = csv.reader(csv_file)
            rows = list(reader)
            return len(rows) > 1 and len(rows[0]) > 1
        except csv.Error:
            return False


@dataclass
class XMLNode:
    tag: str
    attributes: Dict[str, str]
    text: Optional[str]
    children: List["XMLNode"]


class XMLFormatStrategy(FormatStrategy):

    def __init__(self, preserve_whitespaces: bool = False):
        self.preserve_whitespaces = preserve_whitespaces

    def parse_string(self, xml_string: str) -> XMLNode:
        root = ET.fromstring(xml_string)
        return self._parse_element(root)

    def _parse_element(self, element: ET.Element) -> XMLNode:
        text = element.text
        if text and not self.preserve_whitespaces:
            text = text.strip()
            if not text:
                text = None

        node = XMLNode(
            tag=element.tag,
            attributes=dict(element.attrib),
            text=text,
            children=[]
        )

        for child in element:
            node.children.append(self._parse_element(child))
        return node

    def to_dict(self, node: XMLNode) -> Dict:
        result = {
            'tag': node.tag,
            'attributes': node.attributes
        }

        if node.text:
            result['text'] = node.text

        if node.children:
            children_by_tag = defaultdict(list)
            for child in node.children:
                children_by_tag[child.tag].append(self.to_dict(child))

            result['children'] = {
                tag: children[0] if len(children) == 1 else children
                for tag, children in children_by_tag.items()
            }

        return result

    def is_format(content: str) -> bool:
        """
        Checks if the given content is a valid XML format.

        Args:
            content (str): The string content to validate as XML.

        Returns:
            bool: True if the content is valid XML format, False otherwise.

        Example:
            >>> is_format('<root><child>text</child></root>')
            True
            >>> is_format('invalid xml')
            False
        """
        try:
            ET.fromstring(content)
            return True
        except ET.ParseError:
            return False

    def format(self, raw_result: str) -> Dict:
        root_node = self.parse_string(raw_result)
        return self.to_dict(root_node)


class SarifFormatStrategy(FormatStrategy):

    def is_format(raw_result: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_result)
            return (
                isinstance(data, dict)
                and "version" in data
                and data.get("$schema", "").find("sarif") > -1
                and "runs" in data
            )
        except (json.decoder.JSONDecodeError, TypeError, KeyError):
            return False

    def format(self, raw_result) -> Dict[str, Any]:
        sarif_json = json.loads(raw_result)
        return sarif_json


class PlainTextFormatStrategy(FormatStrategy):

    def is_format(content: str) -> bool:
        return isinstance(content, str)

    def format(self, raw_result: str) -> Dict:
        return raw_result


class FormatStrategyFactory:
    strategies = [
        JSONFormatStrategy,
        CSVFormatStrategy,
        XMLFormatStrategy,
        SarifFormatStrategy,
        PlainTextFormatStrategy,
    ]

    @classmethod
    def get_strategy(cls, raw_result: str) -> FormatStrategy:
        """
        Returns an appropriate formatting strategy based on the raw result string.

        This class method analyzes the raw_result string and returns a concrete FormatStrategy
        implementation that can handle the formatting of that specific content type.
        If no matching strategy is found, defaults to PlainTextFormatStrategy.

        Args:
            raw_result (str): The raw string to be analyzed and formatted

        Returns:
            FormatStrategy: A concrete formatting strategy instance that can handle the content

        Example:
            strategy = ToolStrategyOutput.get_strategy('{"key": "value"}')
            # Returns JSONFormatStrategy if the content is valid JSON
        """
        for strategy in cls.strategies:
            if strategy.is_format(raw_result):
                return strategy()
        return PlainTextFormatStrategy()


class StringToolFormatter:
    @staticmethod
    def from_str_to_dict(raw_result: str):
        """
        Convert a raw string result into a dictionary using the appropriate format strategy.

        This function determines the format strategy based on the input string and applies
        the formatting to convert the string into a structured dictionary.

        Args:
            raw_result (str): The raw string result to be converted into a dictionary.

        Returns:
            dict: The formatted dictionary representation of the raw string input.

        Example:
            >>> raw_str = '{"key": "value"}'
            >>> result = from_str_to_dict(raw_str)
            >>> print(result)
            {'key': 'value'}
        """
        strategy = FormatStrategyFactory.get_strategy(raw_result)
        return strategy.format(raw_result)
