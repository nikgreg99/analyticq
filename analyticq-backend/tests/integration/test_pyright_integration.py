import pytest
from analyticq.engine.core.models import (AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel)
from analyticq.engine.tools import PyrightTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary Python file with type errors for pyright to detect."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "test_sample.py"

    # Create a sample Python file with pyright issues (type errors)
    test_code = """
from typing import List, Dict, Optional

def untyped_function(param):
    # Missing type annotations
    return param + 1

def incorrect_return_type() -> str:
    # Type error: Function returns int, but is annotated to return str
    return 42

def type_mismatch(x: int) -> int:
    # Type error: Adding int and str
    return x + "string"

def optional_confusion(maybe_string: Optional[str]) -> str:
    # Type error: maybe_string could be None, but we're returning it as str
    return maybe_string

def list_issues() -> None:
    numbers: List[int] = [1, 2, 3]
    # Type error: Appending str to List[int]
    numbers.append("four")

    # Incompatible types
    mapping: Dict[str, int] = {"one": 1}
    # Type error: 2 is not a str
    mapping[2] = 2
    """
    test_file.write_text(test_code)
    return code_dir


@pytest.fixture(scope="module")
def pyright_tool():
    """Initialize and configure PylintTool with test settings."""
    tool = PyrightTool()
    # Reduce timeout for test environment
    return tool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_pyright_analysis(sample_code, pyright_tool):
    try:

        await pyright_tool.install()

        # 2. Run analysis on sample code
        results = await pyright_tool.run_scan(
            codebase_path=str(sample_code),
        )
        print(results)

        isinstance(results, AnalyticQSASTScanResultModel)

        assert len(results.issues) >= 0

        for issue in results.issues:
            isinstance(issue, AnalyticQSASTIssueModel)

        assert "tool_name" in results.scan_metadata
        assert "metrics" in results.scan_metadata
        assert results.scan_metadata["tool_name"] == "pyright"

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
