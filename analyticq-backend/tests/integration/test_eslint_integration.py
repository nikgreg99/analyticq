import pytest
from analyticq.engine.core.models import (AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel)
from analyticq.engine.tools import EslintTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def eslint_tool():
    """Initialize and configure EslintkTool with test settings."""
    tool = EslintTool()
    return tool


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary JavaScript file with known ESLint violations."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "test_sample.js"

    test_code = """// Common ESLint violations for testing

// no-unused-vars: Variable defined but never used
function unusedFunction(unusedParam) {
    const unusedVar = 'never used';
    return 42;
}

// no-undef: Using undefined variable
function useUndefinedVar() {
    return undefinedVar + 5;
}

// no-var: Using var instead of let/const
var oldVar = 'should use let or const';

// eqeqeq: Not using strict equality
function looseEquality(a, b) {
    return a == b; // should use ===
}

// no-empty: Empty block statement
function emptyFunction() {
    if (true) {
        // Empty block
    }
}

// no-redeclare: Variable redeclaration
function redeclareVariable() {
    var x = 1;
    var x = 2; // redeclaration of x
}

// no-constant-condition: Constant condition in an if statement
function constantCondition() {
    if (true) {
        return 'always true';
    }
}

// semi: Missing semicolon
function missingSemicolon() {
    return 42
}

// no-unreachable: Unreachable code after return
function unreachableCode() {
    return true;
    console.log('unreachable code'); // Unreachable
}

// no-compare-neg-zero: Comparing to -0
function compareToNegativeZero(value) {
    return value === -0;
}

// no-useless-escape: Unnecessary escape character
const regex = /\a/;

// no-console: Console statement
function logToConsole() {
    console.log('This should not be in production');
}

// prefer-const: Let variable that never changes
function preferConst() {
    let x = 5; // should be const
    return x;
}

// curly: Missing curly braces
function missingCurlyBraces(condition) {
    if (condition)
        return true;
    else
        return false;
}

// no-param-reassign: Reassigning function parameter
function reassignParam(param) {
    param = 5; // reassignment of function parameter
    return param;
}

// no-prototype-builtins: Calling Object.prototype methods directly
function objectPrototypeCall(obj, prop) {
    return obj.hasOwnProperty(prop);
}

// Default export and main function
export default function main() {
    return 'ESLint test code';
}
"""
    # Create package.json with ESLint config
    package_json = code_dir / "package.json"
    package_json_content = """{
  "name": "eslint-test",
  "version": "1.0.0",
  "description": "Test project for ESLint",
  "main": "test_sample.js",
  "eslintConfig": {
    "env": {
      "browser": true,
      "es2021": true,
      "node": true
    },
    "extends": "eslint:recommended",
    "parserOptions": {
      "ecmaVersion": "latest",
      "sourceType": "module"
    },
    "rules": {}
  }
}"""
    # Write files
    test_file.write_text(test_code)
    package_json.write_text(package_json_content)
    return code_dir


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_eslint_analysis(sample_code, eslint_tool):
    """Test full ESLint analysis workflow from code scan to report generation."""
    try:
        # 1. Install the container image
        await eslint_tool.install()

        # 2. Run analysis on sample code
        result = await eslint_tool.run_scan(
            codebase_path=str(sample_code),
        )

        # 3. Verify the basic structure of the result
        assert isinstance(result, AnalyticQSASTScanResultModel)
        assert result.scan_metadata["tool_name"] == "eslint"

        assert len(result.issues) == 0

        for issue in result.issues:
            assert isinstance(issue, AnalyticQSASTIssueModel)

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
