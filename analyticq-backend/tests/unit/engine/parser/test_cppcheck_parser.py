import pytest
from analyticq.engine.core.models import AnalyticQConfidence, AnalyticQSeverity
from analyticq.engine.parser import CppCheckParser
from analyticq.exception import ScanParserException


@pytest.fixture
def cppcheck_parser():
    return CppCheckParser()


@pytest.fixture
def sample_string_xml():
    return """ <?xml version="1.0" encoding="UTF-8"?>
 <results version="2">
 <cppcheck version="1.66"/>
 <errors>
 <error id="someError" severity="error" msg="short error text"
 verbose="long error text" inconclusive="true" cwe="312">
 <location file0="file.c" file="file.h" line="1"/>
 </error>
 </errors>
 </results>"""


@pytest.fixture
def complex_xml_input():
    return {
        'tag': 'results',
        'attributes': {'version': '2'},
        'children': {
            'cppcheck': {'tag': 'cppcheck', 'attributes': {'version': '2.7'}},
            'errors': {
                'children': {
                    'error': [
                        {
                            'attributes': {
                                'id': 'nullPointer',
                                'severity': 'error',
                                'msg': 'Null pointer dereference',
                                'verbose': 'Detailed null pointer message',
                                'cwe': '476'
                            },
                            'children': {
                                'location': [
                                    {
                                        'attributes': {
                                            'file': 'test.cpp',
                                            'line': '42',
                                            'column': '5',
                                            'info': 'Dereferencing occurs here'
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            'attributes': {
                                'id': 'uninitVar',
                                'severity': 'warning',
                                'msg': 'Uninitialized variable',
                                'verbose': 'Variable used without initialization',
                                'cwe': '457'
                            },
                            'children': {
                                'location': {
                                    'attributes': {
                                        'file': 'test.cpp',
                                        'line': '23',
                                        'column': '10'
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
    }


def test_parser_initialization(cppcheck_parser):
    """Test parser initialization and field mapping."""
    assert cppcheck_parser.tool_name == "cppcheck"
    assert cppcheck_parser.field_mapping["rule_id"] == "id"
    assert cppcheck_parser.field_mapping["message"] == "msg"
    assert cppcheck_parser.field_mapping["path"] == "file"


def test_severity_mapping(cppcheck_parser):
    """Test mapping of different severity levels."""
    assert cppcheck_parser._map_severity("error") == AnalyticQSeverity.HIGH
    assert cppcheck_parser._map_severity("warning") == AnalyticQSeverity.MEDIUM
    assert cppcheck_parser._map_severity("style") == AnalyticQSeverity.LOW
    assert cppcheck_parser._map_severity("performance") == AnalyticQSeverity.MEDIUM
    assert cppcheck_parser._map_severity("information") == AnalyticQSeverity.INFO
    assert cppcheck_parser._map_severity("unknown") == AnalyticQSeverity.UNKNOWN


def test_confidence_mapping(cppcheck_parser):
    """Test mapping of confidence levels."""
    assert cppcheck_parser._map_confidence("any") == AnalyticQConfidence.UNKNOWN


def test_loc_parse(cppcheck_parser):
    issue_data = {
        'children': {
            'location': [
                {
                    'attributes': {
                        'file': 'test.cpp',
                        'line': '42',
                        'column': '5',
                        'info': 'Test info'
                    }
                }
            ]
        }
    }

    locs = cppcheck_parser.parse_locations(issue_data)
    assert len(issue_data) == 1
    assert locs[0]['file'] == 'test.cpp'
    assert locs[0]['line'] == '42'
    assert locs[0]['column'] == '5'
    assert locs[0]['info'] == 'Test info'


def test_metadata_handling(cppcheck_parser, complex_xml_input):
    result = cppcheck_parser.parse_scan_result(complex_xml_input)
    first_issue = result.issues[0]

    assert first_issue.metadata["cwe"] == "476"
    assert "help_uri" in first_issue.metadata
    assert len(first_issue.metadata["all_locations"]) == 1


def test_error_parsing(cppcheck_parser):
    with pytest.raises(ScanParserException):
        cppcheck_parser.parse_scan_result({})

    with pytest.raises(ScanParserException):
        cppcheck_parser.parse_scan_result({'invalid': 'structure'})


def test_empty_result_handling(cppcheck_parser):
    input_data = {
        'children': {
            'errors': {
                'children': {
                    'error': []
                }
            }
        }
    }

    with pytest.raises(ScanParserException):
        cppcheck_parser.parse_scan_result(input_data)
