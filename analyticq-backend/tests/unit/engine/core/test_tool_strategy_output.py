import xml.etree.ElementTree as ET
from typing import Dict

import pytest
from analyticq.engine.core import StringToolFormatter, XMLFormatStrategy


@pytest.mark.parametrize(
    "raw_input,expected_output",
    [
        ('{"name": "John", "age": 30}', {"name": "John", "age": 30}),
        ('{"name": "Jane", "age": 25}', {"name": "Jane", "age": 25}),
    ]
)
def test_json_format(raw_input, expected_output):
    result = StringToolFormatter.from_str_to_dict(raw_input)
    assert result == expected_output


@pytest.mark.parametrize(
    "raw_input,expected_output",
    [
        ('name,age\nJohn,30\nJane,25', [
            {"name": "John", "age": "30"},
            {"name": "Jane", "age": "25"}
        ]),
        ('name,age\nAlice,22\nBob,28', [
            {"name": "Alice", "age": "22"},
            {"name": "Bob", "age": "28"}
        ]),
    ]
)
def test_csv_format(raw_input, expected_output):
    result = StringToolFormatter.from_str_to_dict(raw_input)
    assert result == expected_output


@pytest.mark.parametrize(
    "raw_input,expected_output",
    [
        ('This is a plain text message.', "This is a plain text message."),
        ('Another plain text example.', "Another plain text example."),
    ]
)
def test_plain_text_format(raw_input, expected_output):
    result = StringToolFormatter.from_str_to_dict(raw_input)
    assert result == expected_output, f"Expected {expected_output}, got {result}"


@pytest.mark.parametrize(
    "raw_input,expected_output",
    [
        ('{"name": "John", "age": 30}', {"name": "John", "age": 30}),
        ('name,age\nJohn,30\nJane,25', [
            {"name": "John", "age": "30"},
            {"name": "Jane", "age": "25"}
        ]),
        ('This is a plain text message.', "This is a plain text message."),
    ]
)
def test_various_formats(raw_input, expected_output):
    result = StringToolFormatter.from_str_to_dict(raw_input)
    assert result == expected_output, f"Expected {expected_output}, got {result}"


# Test cases
@pytest.mark.parametrize(
    "raw_input,expected_output",
    [
        # Test Case 1: Simple XML with single element
        (
            '''<?xml version="1.0" encoding="UTF-8"?>
            <root>Simple text</root>''',
            {
                "tag": "root",
                "attributes": {},
                "text": "Simple text"
            }
        ),

        # Test Case 2: XML with attributes
        (
            '''<?xml version="1.0" encoding="UTF-8"?>
            <root id="1" type="test">
                <child>Content</child>
            </root>''',
            {
                "tag": "root",
                "attributes": {"id": "1", "type": "test"},
                "children": {
                    "child": {
                        "tag": "child",
                        "attributes": {},
                        "text": "Content"
                    }
                }
            }
        ),

        # Test Case 3: XML with multiple children
        (
            '''<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <child>First</child>
                <child>Second</child>
            </root>''',
            {
                "tag": "root",
                "attributes": {},
                "children": {
                    "child": [
                        {
                            "tag": "child",
                            "attributes": {},
                            "text": "First"
                        },
                        {
                            "tag": "child",
                            "attributes": {},
                            "text": "Second"
                        }
                    ]
                }
            }
        ),

        # Test Case 4: Complex nested XML
        (
            '''<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <person id="1">
                    <name>John</name>
                    <contacts>
                        <email>john@example.com</email>
                        <phone>123-456-7890</phone>
                    </contacts>
                </person>
            </root>''',
            {
                "tag": "root",
                "attributes": {},
                "children": {
                    "person": {
                        "tag": "person",
                        "attributes": {"id": "1"},
                        "children": {
                            "name": {
                                "tag": "name",
                                "attributes": {},
                                "text": "John"
                            },
                            "contacts": {
                                "tag": "contacts",
                                "attributes": {},
                                "children": {
                                    "email": {
                                        "tag": "email",
                                        "attributes": {},
                                        "text": "john@example.com"
                                    },
                                    "phone": {
                                        "tag": "phone",
                                        "attributes": {},
                                        "text": "123-456-7890"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
    ]
)
def test_xml_format(raw_input: str, expected_output: Dict):
    result = StringToolFormatter.from_str_to_dict(raw_input)
    assert result == expected_output, "Expected equality"


# Test error handling
def test_invalid_xml():
    formatter = XMLFormatStrategy()
    with pytest.raises(ET.ParseError):
        formatter.format("<invalid>XML<invalid>")
