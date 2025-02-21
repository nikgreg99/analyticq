import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.engine.tools.python.pylint import PylintTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary Python file with known Pylint violations."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "test_sample.py"

    # Create a sample Python file with known Pylint issues
    test_code = """
def bad_function(x, y = None):
    # C0103: Variable name "a" doesn't conform to snake_case naming style
    a = x + 1

    # W0613: Unused argument 'y'
    # R1705: Unnecessary "else" after "return"
    if x > 0:
        return a
    else:
        return x

# C0116: Missing function docstring
def another_bad_function():
    # W0612: Unused variable 'unused'
    unused = 42
    return True
    """
    test_file.write_text(test_code)
    return code_dir


@pytest.fixture(scope="module")
def pylint_tool():
    """Initialize and configure PylintTool with test settings."""
    tool = PylintTool()
    # Reduce timeout for test environment
    return tool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_pylint_analysis(sample_code, pylint_tool):
    try:

        await pylint_tool.install()

        # 2. Run analysis on sample code
        results = await pylint_tool.run_scan(
            codebase_path=str(sample_code),
        )
        print(results)

        # 3. Validate results structure
        assert isinstance(results, AnalyticQSASTScanResult), "Invalid results type"
        assert len(results.issues) >= 5, "Should find at least 5 issues"

        # 4. Verify specific findings
        expected_issues = {
            "W0613": False,  # Unused argument
            "R1705": False,  # Unnecessary else
            "C0116": False,  # Missing function or method docstring
            "C0114": False,  # Missing module docstring
            "W0612": False,  # Unused variable
            "W0613": False   # Unused argument
        }

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssue)
            assert issue.path.endswith("test_sample.py")

            if issue.rule_id in expected_issues:
                expected_issues[issue.rule_id] = True

                # Verify severity mappings
                if issue.rule_id.startswith("C"):
                    assert issue.severity == AnalyticQSeverity.LOW
                elif issue.rule_id.startswith("W"):
                    assert issue.severity == AnalyticQSeverity.MEDIUM
                elif issue.rule_id.startswith("R"):
                    assert issue.severity == AnalyticQSeverity.LOW

                # Verify confidence levels
                assert issue.confidence in [
                    AnalyticQConfidence.UNKNOWN,
                ]

        for rule_id, found in expected_issues.items():
            assert found, f"Missing {rule_id} issue"

        assert results.summary["total"] >= 5
        assert results.summary["by_severity"]["LOW"] >= 2
        assert results.summary["by_severity"]["MEDIUM"] >= 1

        assert "tool_name" in results.metadata
        assert "metrics" in results.metadata
        assert results.metadata["tool_name"] == "Pylint"

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
