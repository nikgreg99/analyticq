import pytest
from analyticq.engine.core.models import (AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel)
from analyticq.engine.tools import NjsscanTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def njsscan_tool():
    """Initialize and configure GosecTool with test settings."""
    tool = NjsscanTool()
    # Reduce timeout for test environment
    tool.container_manager.runtime_config.timeout = 120
    return tool


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    code_dir = tmp_path_factory.mktemp("code")

    # Create package.json
    package_json = code_dir / "package.json"
    package_json_content = """{
        "name": "vulnerable-node-app",
        "version": "1.0.0",
        "description": "Test app with security vulnerabilities",
        "main": "app.js"
    }"""
    package_json.write_text(package_json_content)

    # Create app.js with insecure session settings
    app_js = code_dir / "app.js"
    app_js_content = """
const express = require('express');
const session = require('express-session');
const app = express();

// CWE-614: Insecure cookie flag (missing secure flag)
app.use(session({
    secret: 'keyboard cat',
    resave: false,
    saveUninitialized: true,
    cookie: {}  // Missing secure:true
}));

app.get('/', (req, res) => {
    res.send('Hello World!');
});

// CWE-798: Hard-coded credentials
const password = "SuperSecretPassword123";

// Start the server
app.listen(3000, () => {
    console.log('Server started on port 3000');
});
"""
    app_js.write_text(app_js_content)

    # Create a file with NoSQL injection vulnerability
    nosql_js = code_dir / "nosql.js"
    nosql_js_content = """
const express = require('express');
const mongodb = require('mongodb');
const router = express.Router();

// CWE-943: NoSQL Injection
router.get('/users', async (req, res) => {
    const db = await mongodb.connect('mongodb://localhost:27017/test');
    const collection = db.collection('users');

    // Insecure: directly using user input in query
    const query = { username: req.query.username };
    const user = await collection.findOne(query);

    res.json(user);
});

module.exports = router;
"""
    nosql_js.write_text(nosql_js_content)

    # Create a file with unsafe regular expressions
    regex_js = code_dir / "regex.js"
    regex_js_content = """
const express = require('express');
const router = express.Router();

// CWE-400: Regex Denial of Service (ReDoS)
router.get('/validate', (req, res) => {
    const userInput = req.query.input;

    // Vulnerable regex pattern (exponential backtracking)
    const emailRegex = /^([a-zA-Z0-9_\\-\\.]+)@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.)|(([a-zA-Z0-9\\-]+\\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$/;

    const isValid = emailRegex.test(userInput);
    res.json({ valid: isValid });
});

module.exports = router;
"""
    regex_js.write_text(regex_js_content)

    # Create a file with command injection vulnerability
    cmd_js = code_dir / "command.js"
    cmd_js_content = """
const express = require('express');
const { exec } = require('child_process');
const router = express.Router();

// CWE-78: OS Command Injection
router.get('/ping', (req, res) => {
    const host = req.query.host;

    // Insecure: directly using user input in command
    exec('ping -c 4 ' + host, (error, stdout, stderr) => {
        if (error) {
            res.status(500).send(stderr);
            return;
        }
        res.send(stdout);
    });
});

module.exports = router;
"""
    cmd_js.write_text(cmd_js_content)

    return code_dir


@pytest.mark.asyncio
@pytest.mark.integration
async def test_njjscan_integration(njsscan_tool, sample_code):
    try:
        await njsscan_tool.install()

        # Run analysis on sample code
        results = await njsscan_tool.run_scan(
            codebase_path=str(sample_code),
        )

        assert isinstance(results, AnalyticQSASTScanResultModel), "Invalid results type"
        assert len(results.issues) >= 4, "Should find at least 4 issues"

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssueModel)

        # Verify scan metadata
        assert results.summary["total"] >= 4
        assert "tool_name" in results.scan_metadata
        assert results.scan_metadata["tool_name"] == "njsscan"
        assert "metrics" in results.scan_metadata

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
