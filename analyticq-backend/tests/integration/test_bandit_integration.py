# tests/test_bandit_integration.py
import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.engine.tools.python.bandit import BanditTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary Python file with known vulnerabilities."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "test_sample.py"

    # Create a sample Python file with known Bandit issues
    test_code = """
def insecure_function():
    # B105: Hardcoded password
    password = "secret"  # nosec
    # B101: assert used
    assert password == "secret"
    return password
    """
    test_file.write_text(test_code)
    return code_dir


@pytest.fixture(scope="module")
def bandit_tool():
    """Initialize and configure BanditTool with test settings."""
    tool = BanditTool()
    # Reduce timeout for test environment
    tool.container_manager.runtime_config.timeout = 120
    return tool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_bandit_analysis(sample_code, bandit_tool):
    """Test full Bandit analysis workflow from code scan to report generation."""
    try:
        # 1. Install the container image
        await bandit_tool.install()

        # 2. Run analysis on sample code
        results = await bandit_tool.run_scan(
            codebase_path=str(sample_code),
        )

        # 3. Validate results structure
        assert isinstance(results, AnalyticQSASTScanResult), "Invalid results type"
        assert len(results.issues) >= 2, "Should find at least 2 issues"

        # 4. Verify specific findings
        found_b101 = False
        found_b105 = False

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssue)
            assert issue.path.endswith("test_sample.py")

            if issue.rule_id == "B101":
                found_b101 = True
                assert issue.severity == AnalyticQSeverity.LOW
                assert issue.start_line > 5  # Line number in sample code

            if issue.rule_id == "B105":
                found_b105 = True
                assert issue.severity == AnalyticQSeverity.LOW
                assert issue.confidence == AnalyticQConfidence.MEDIUM

        assert found_b101, "Missing B101 (assert used) finding"
        assert found_b105, "Missing B105 (hardcoded password) finding"

        # 5. Validate summary
        assert results.summary["total"] >= 2
        assert results.summary["by_severity"]["LOW"] >= 1

        # 6. Validate metadata
        assert "tool" in results.metadata
        assert "metrics" in results.metadata

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")


# Add Docker availability check
def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
