import csv
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from io import StringIO
from typing import Any, ClassVar, Dict, List, Optional, Union

SCHEMA_IDENTIFIERS = [
    "sarif",
    "sarifv1",
    "sarifv2"
]


class OutputFormat(Enum):
    """
    Enumeration class representing different output formats for tool strategy results.

    The OutputFormat enum defines supported file formats for exporting/storing analysis results.

    Values:
        JSON: JavaScript Object Notation format
        CSV: Comma Separated Values format
        XML: Extensible Markup Language format
        SARIF: Static Analysis Results Interchange Format
        PLAIN: Plain text format. The default one
    """
    JSON = auto()
    CSV = auto()
    XML = auto()
    SARIF = auto()
    PLAIN = auto()

    def __str__(self) -> str:
        return self.name.lower()


class FormatStrategy(ABC):
    """Abstract base class defining a strategy pattern for formatting results.

    This class serves as an interface for different formatting strategies that can be
    applied to raw results from various tools or processes.

    Methods
    -------
    format(raw_result: str) -> Union[Dict, list]
        Abstract method that formats a raw string result into either a dictionary or list.
        Must be implemented by concrete strategy classes.

    is_format(content: str) -> bool
        Static method to check if content matches the format.
        Default implementation returns False.
        Should be overridden by concrete strategy classes to provide actual format validation.

    Notes
    -----
    All concrete format strategy classes should inherit from this abstract base class
    and implement the format() method according to their specific formatting requirements.
    """
    @abstractmethod
    def format(self, raw_result: str) -> Union[Dict, list]:
        """
        Formats the raw output result from a tool execution.

        Args:
            raw_result (str): The raw string output from executing a tool.

        Returns:
            Union[Dict, list]: The formatted result as either a dictionary or list structure.

        Raises:
            None

        Example:
            >>> strategy = ToolStrategyOutput()
            >>> raw = "some tool output"
            >>> formatted = strategy.format(raw)
        """
        pass

    @staticmethod
    def is_format(content: str) -> bool:
        """
        Check if a string content matches a specific format.

        Args:
            content (str): The string content to check format for.

        Returns:
            bool: False by default, indicating no format validation is implemented.
        """
        return False


class JSONFormatStrategy(FormatStrategy):
    """ A strategy class for handling JSON format conversion operations.

    This class implements the FormatStrategy interface to handle JSON-specific formatting operations,
    providing methods to validate and parse JSON-formatted strings into Python data structures.

    Methods:
        format(raw_result: str) -> Union[Dict, list]:
            Converts a JSON-formatted string into a Python dictionary or list.

        is_format(content: str) -> bool:
            Validates whether a given string is in valid JSON format.
    """

    def format(self, raw_result: str) -> Union[Dict, list]:
        """
        Formats raw string result into a Python dictionary or list.

        This method attempts to parse a JSON-formatted string into a Python data structure.

        Args:
            raw_result (str): JSON-formatted string to be parsed

        Returns:
            Union[Dict, list]: Parsed Python dictionary or list object

        Raises:
            json.JSONDecodeError: If the input string is not valid JSON
        """
        try:
            return json.loads(raw_result)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}") from e

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
        if not isinstance(content, str):
            return False

        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, TypeError):
            return False


class CSVFormatStrategy(FormatStrategy):
    """
    A strategy class for formatting CSV data strings into structured data.
    This class implements the FormatStrategy interface and provides methods to format
    CSV string data into a list of dictionaries and validate CSV formatted content.
    Methods:
        format(raw_result: str) -> list:
            Converts a CSV string into a list of dictionaries.
        is_format(content: str) -> bool:
            Validates if a string contains properly formatted CSV data.
    """
    def format(self, raw_result: str) -> list:
        """
        Formats raw CSV string data into a list of dictionaries.

        This method takes a raw CSV string, converts it into a CSV-like object using StringIO,
        and returns a list where each element is a dictionary representing a row from the CSV,
        with column headers as keys.

        Args:
            raw_result (str): A string containing CSV formatted data.

        Returns:
            list: A list of dictionaries where each dictionary represents a row from the CSV data,
                  with column headers as keys and row values as values.

        Example:
            If raw_result is:
            "name,age\nJohn,30\nJane,25"

            The output will be:
            [
                {'name': 'John', 'age': '30'},
                {'name': 'Jane', 'age': '25'}
            ]
        """
        try:
            csv_file = StringIO(raw_result)
            reader = csv.DictReader(csv_file)

            # Verify headers exist
            if not reader.fieldnames:
                raise ValueError("CSV has no headers")

            result = list(reader)

            # Check if any rows were parsed
            if not result:
                raise ValueError("CSV has no data rows")

            return result
        except csv.Error as e:
            raise ValueError(f"CSV parsing error: {e}") from e

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
        if not isinstance(content, str):
            return False

        try:
            csv_file = StringIO(content)
            reader = csv.reader(csv_file)
            rows = list(reader)

            return len(rows) > 1 and len(rows[0]) > 1
        except (csv.Error, TypeError):
            return False


@dataclass
class XMLNode:
    tag: str
    attributes: Dict[str, str]
    text: Optional[str]
    children: List["XMLNode"]


class XMLFormatStrategy(FormatStrategy):
    """
    A strategy class for parsing and formatting XML content.

    This class implements the FormatStrategy interface to handle XML-specific formatting operations.
    It provides functionality to parse XML strings into a tree structure of XMLNode objects and
    convert them back to dictionary representations.

        preserve_whitespaces (bool, optional): If True, preserves whitespace in text content.
            If False, strips whitespace from text content. Defaults to False.

    Attributes:
        preserve_whitespaces (bool): Flag indicating whether to preserve whitespace in text content.

    Methods:
        parse_string(xml_string: str) -> XMLNode:
            Parses an XML string into an XMLNode tree structure.

        _parse_element(element: ET.Element) -> XMLNode:
            Internal method to recursively parse XML elements into XMLNode objects.

        to_dict(node: XMLNode) -> Dict:
            Converts an XMLNode tree structure into a dictionary representation.

        is_format(content: str) -> bool:
            Validates if a given string is valid XML content.

        format(raw_result: str) -> Dict:
            Formats raw XML string into a dictionary representation.

        >>> formatter = XMLFormatStrategy()
        >>> result = formatter.format('<root><child>text</child></root>')
        >>> print(result)
        {
            'tag': 'root',
            'attributes': {},
            'children': {
                'child': {
                    'tag': 'child',
                    'attributes': {},
                    'text': 'text'
    """
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
        if not isinstance(content, str):
            return False

        try:
            ET.fromstring(content)
            return True
        except ET.ParseError:
            return False

    def format(self, raw_result: str) -> Dict:
        root_node = self.parse_string(raw_result)
        return self.to_dict(root_node)


class SarifFormatStrategy(FormatStrategy):
    """A strategy class for handling SARIF (Static Analysis Results Interchange Format) output.

    This class implements the FormatStrategy interface to process SARIF-formatted results.
    SARIF is a standard JSON-based format for static analysis tools to report results.

    Methods:
        is_format(raw_result: str) -> Dict[str, Any]:
            Determines if the input string is in valid SARIF format.

            Args:
                raw_result (str): The raw string to be checked.

            Returns:
                bool: True if the input is valid SARIF format, False otherwise.

        format(raw_result: str) -> Dict[str, Any]:
            Converts the raw SARIF string into a parsed dictionary.

            Args:
                raw_result (str): The raw SARIF string to be formatted.

            Returns:
                Dict[str, Any]: The parsed SARIF data as a dictionary.

            Raises:
                json.decoder.JSONDecodeError: If the input string is not valid JSON.
    """

    SCHEMA_IDENTIFIERS: ClassVar[List[str]] = [
        "sarif",
        "sarifv1",
        "sarifv2"
    ]

    def is_format(raw_result: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_result)
            has_version = "version" in data
            has_runs = "runs" in data and isinstance(data["runs"], list)

            # Check for SARIF schema identifier
            schema_ref = data.get("$schema", "")
            has_sarif_schema = any(ident in schema_ref for ident in SCHEMA_IDENTIFIERS)

            return has_version and has_runs and has_sarif_schema
        except (json.decoder.JSONDecodeError, TypeError, KeyError):
            return False

    def format(self, raw_result) -> Dict[str, Any]:
        try:
            sarif_json = json.loads(raw_result)

            if not self.is_format(raw_result):
                raise ValueError("Content is valid JSON but not in SARIF format")
            return sarif_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in SARIF document: {e}") from e


class PlainTextFormatStrategy(FormatStrategy):

    def is_format(content: str) -> bool:
        """
        Check if the content is in string format.

        Args:
            content (str): The content to be checked.

        Returns:
            bool: True if content is a string, False otherwise.
        """
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
        if not isinstance(raw_result, str):
            raise TypeError(f"Expected string input, got {type(raw_result).__name__}")

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
