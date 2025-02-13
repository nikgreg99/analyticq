from typing import Any, Dict

import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.exception import ScanParserException

from .staticcheck_parser import StaticCheckParser  # noqa


@pytest.fixture
def parser():
    return StaticCheckParser()

@pytest.fixture
def valid_raw_result():
    return [{
        "severity": "error",
        "code": "TEST001",
        "message": "Test error message",
        "location": {
            "file": "/path/to/file.py",
            "line": 10
        },
        "end": {
            "line": 15
        }
    }]


def test_metadata(parser):
    result = parser.s([])

    assert result.metadata["tool"] == "StaticCheck"
    assert isinstance(result.metadata["metrics"], dict)
    assert len(result.metadata["metrics"]) == 0
