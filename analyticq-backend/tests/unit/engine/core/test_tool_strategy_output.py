import pytest
from analyticq.engine.core import StringToolFormatter


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
        ('This is a plain text message.', {"content": "This is a plain text message."}),
        ('Another plain text example.', {"content": "Another plain text example."}),
    ]
)
def test_plain_text_format(raw_input, expected_output):
    result = StringToolFormatter.from_str_to_dict(raw_input)
    assert result == expected_output


@pytest.mark.parametrize(
    "raw_input,expected_output",
    [
        ('{"name": "John", "age": 30}', {"name": "John", "age": 30}),
        ('name,age\nJohn,30\nJane,25', [
            {"name": "John", "age": "30"},
            {"name": "Jane", "age": "25"}
        ]),
        ('This is a plain text message.', {"content": "This is a plain text message."}),
    ]
)
def test_various_formats(raw_input, expected_output):
    result = StringToolFormatter.from_str_to_dict(raw_input)
    assert result == expected_output
