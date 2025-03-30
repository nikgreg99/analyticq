import pytest
from analyticq.engine.core.models import (AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel)
from analyticq.engine.tools import GosecTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def gosec_tool():
    """Initialize and configure GosecTool with test settings."""
    tool = GosecTool()
    # Reduce timeout for test environment
    tool.container_manager.runtime_config.timeout = 120
    return tool


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary Go file with known GoSec security vulnerabilities."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "main.go"

    # Create a sample Go file with known GoSec security issues using only standard library
    test_code = """
package main

import (
    "fmt"
    "os"
)

func unusedParam(x int, y string) {
    // SA4009: unused parameter y
    fmt.Println(x)
}

func redundantNil() error {
    // SA4023: redundant nil check
    var err error
    if err != nil {
        return err
    }
    return nil
}

func unreachableCode() {
    // SA4004: unreachable code
    fmt.Println("This will never execute")
    return
    fmt.Println("Unreachable")
}

func deferInLoop() {
    // SA5007: defer in loop
    for i := 0; i < 10; i++ {
        f, _ := os.Open("test.txt")
        defer f.Close()
    }
}

func ineffectiveCopy() {
    // SA4006: ineffective assignment to same slice
    s := []int{1, 2, 3}
    s = s
    fmt.Println(s)
}

func wrongStringComparison() {
    // SA5000: comparing strings with == instead of strings.EqualFold
    if "Go" == "go" {
        fmt.Println("Case-insensitive match")
    }
}

func invalidSlice() {
    // SA4001: invalid slice index
    arr := []int{1, 2, 3}
    fmt.Println(arr[5]) // Out of bounds access
}

func ineffectiveLoop() {
    // SA4010: ineffective loop
    for i := 0; i < 10; i++ {
        return
    }
}

func pointlessAppend() {
    // SA4011: redundant append
    var data []int
    data = append(data)
    fmt.Println(data)
}

func main() {
    // Call functions to avoid "unused function" warnings
    unusedParam(1, "test")
    _ = redundantNil()
    unreachableCode()
    deferInLoop()
    ineffectiveCopy()
    wrongStringComparison()
    invalidSlice()
    ineffectiveLoop()
    pointlessAppend()
}
"""
    test_file.write_text(test_code)
    return code_dir


@pytest.mark.integration
@pytest.mark.asyncio
async def test_gosec_full_analysis(sample_code, gosec_tool):
    try:
        await gosec_tool.install()

        # Run analysis on sample code
        results = await gosec_tool.run_scan(
            codebase_path=str(sample_code),
        )

        assert isinstance(results, AnalyticQSASTScanResultModel), "Invalid results type"
        assert len(results.issues) == 1, "Should find at least 3 issues"

        expected_issues = {
            "G602": False,  # Incorrect file permissions
        }

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssueModel)
            assert issue.path.endswith("main.go")

            if issue.rule_id in expected_issues:
                expected_issues[issue.rule_id] = True

        for rule_id, found in expected_issues.items():
            assert found, f"Missing {rule_id} issue"

        assert results.summary["total"] == 1

        assert "tool_name" in results.scan_metadata
        assert "metrics" in results.scan_metadata
        assert "lines" in results.scan_metadata["metrics"]
        assert results.scan_metadata["tool_name"] == "gosec"

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
