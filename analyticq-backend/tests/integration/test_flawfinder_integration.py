import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssue,
                                          AnalyticQSASTScanResult,
                                          AnalyticQSeverity)
from analyticq.engine.tools.c.flawfinder import FlawFinderTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary C file with known vulnerabilities."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "test_sample.c"

    # Create a sample C file with known Flawfinder issues
    test_code = """
    #include <stdio.h>
    #include <string.h>

    int main() {
        char buffer[100];
        // CWE-120: Buffer Copy without Checking Size of Input
        gets(buffer);

        char destination[50];
        char source[100] = "This is a very long string that might cause buffer overflow";
        // CWE-119: Buffer Copy without Checking Size of Input
        strcpy(destination, source);

        // CWE-134: Use of Externally-Controlled Format String
        printf(buffer);

        return 0;
    }
    """
    test_file.write_text(test_code)
    return code_dir


@pytest.fixture(scope="module")
def flawfinder_tool():
    """Initialize and configure FlawfinderTool with test settings."""
    tool = FlawFinderTool()
    # Reduce timeout for test environment
    tool.container_manager.runtime_config.timeout = 120
    return tool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_flawfinder_analysis(sample_code, flawfinder_tool):
    """Test full Flawfinder analysis workflow from code scan to report generation."""
    try:
        # 1. Install the container image
        await flawfinder_tool.install()

        # 2. Run analysis on sample code
        results = await flawfinder_tool.run_scan(
            codebase_path=str(sample_code),
        )

        # 3. Validate results structure
        assert isinstance(results, AnalyticQSASTScanResult), "Invalid results type"
        assert len(results.issues) >= 3, "Should find at least 3 issues"

        # 4. Verify specific findings
        found_gets = False
        found_strcpy = False

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssue)
            assert issue.path.endswith("test_sample.c")

            if "gets" in issue.message.lower():
                found_gets = True
                assert issue.severity == AnalyticQSeverity.CRITICAL
                assert issue.confidence == AnalyticQConfidence.UNKNOWN

            if "strcpy" in issue.message.lower():
                found_strcpy = True
                assert issue.severity == AnalyticQSeverity.HIGH

        assert found_gets, "Missing gets() vulnerability finding"
        assert found_strcpy, "Missing strcpy() vulnerability finding"

        assert results.summary["total"] >= 3
        assert results.summary["by_severity"]["HIGH"] >= 1
        assert results.summary["by_severity"]["CRITICAL"] >= 1

        assert "tool_name" in results.metadata
        assert "metrics" in results.metadata

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
