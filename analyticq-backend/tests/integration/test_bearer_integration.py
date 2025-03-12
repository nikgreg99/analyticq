import pytest
from analyticq.engine.core.models import (AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel)
from analyticq.engine.tools import BearerTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create temporary files with known Bearer security issues."""
    code_dir = tmp_path_factory.mktemp("code")

    # JavaScript file with security issues
    js_file = code_dir / "app.js"
    js_code = """
    const express = require('express');
    const app = express();

    app.get('/users', (req, res) => {
        const userId = req.query.id;

        const query = `SELECT * FROM users WHERE id = ${userId}`;

        res.json({success: true});
    });

    const apiKey = "ak_live_1234567890abcdef";
    const password = "super_secret_password";

    app.listen(3000);
    """
    js_file.write_text(js_code)

    # Python file with security issues
    py_file = code_dir / "api.py"
    py_code = """
    import requests

    def get_user_data(user_id):
        # SENSITIVE-DATA: Hardcoded token
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example"

        # INSECURE-REQUESTS: Missing certificate validation
        response = requests.get(
            f"https://api.example.com/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            verify=False
        )
        return response.json()
    """
    py_file.write_text(py_code)

    return code_dir


@pytest.fixture(scope="module")
def bearer_tool():
    """Initialize and configure BearerTool with test settings."""
    tool = BearerTool()
    return tool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_bearer_analysis(sample_code, bearer_tool):
    """Test full Bearer analysis workflow from code scan to report generation."""
    try:
        # 1. Install the Bearer CLI
        await bearer_tool.install()

        # 2. Run analysis on sample code
        results = await bearer_tool.run_scan(
            codebase_path=str(sample_code),
        )

        # 3. Validate results structure
        assert isinstance(results, AnalyticQSASTScanResultModel), "Invalid results type"
        assert len(results.issues) >= 4, "Should find at least 4 issues"

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssueModel)

        # 5. Validate summary
        assert results.summary["total"] >= 4
        assert results.summary["by_severity"]["HIGH"] >= 1
        assert results.summary["by_severity"]["MEDIUM"] >= 1

        # 6. Validate metadata
        assert "tool_name" in results.scan_metadata
        assert results.scan_metadata["tool_name"] == "bearer"
        assert "metrics" in results.scan_metadata

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
