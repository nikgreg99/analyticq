import pytest
from analyticq.engine.tools import FlakeTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary Python file with known Flake8 issues."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "test_flake8_sample.py"

    # Create a sample Python file with known Flake8 issues
    # Code sample generated for test purposes
    test_code = """
import os, sys, json

# E302: Expected 2 blank lines
class FlakeTest:
    # E111: Indentation is not a multiple of 4 (using 2 spaces instead of 4)
  def improperly_indented(self):
      return "This method has a properly indented line"

    # E201: Whitespace after '(' and E202: Whitespace before ')'
    def extra_whitespace( self ):
        # E225: Missing whitespace around operator
        x=1+2

        # E231: Missing whitespace after ','
        items = [1,2,3,4]

        # E251: Unexpected spaces around keyword parameter equals
        self.function(param = 1)

        # E261: At least two spaces before inline comment
        x = 5# This comment is too close

        # W291: Trailing whitespace
        trailing_space = "This line ends with whitespace" # noqa

        # E501: Line too long
        very_long_string = "This is an extremely long line that definitely exceeds the standard 79 character limit set by PEP 8 for maximum line length in Python code."

        return x


# F841: Local variable is assigned but never used
def unused_variables():
    unused_var = "This variable is never used"
    return "Function result"


# F401: Module imported but unused
import datetime


# E303: Too many blank lines (3)



# F811: Redefinition of unused name
def duplicate_function():
    return "Original function"

def duplicate_function():  # This redefines the previous function
    return "Duplicate function"


# E305: Expected 2 blank lines after function definition
def no_blank_lines_after():
    pass
class TooClose:  # Should have 2 blank lines before this class
    pass


# W293: Blank line contains whitespace
def blank_line_with_spaces():

    return "Function with a blank line containing spaces above"


# F821: Undefined name
def undefined_variable():
    return undefined_name  # This variable is not defined


# E711: Comparison to None should be 'if cond is None:'
def compare_to_none(value):
    if value == None:  # Should use 'is None'
        return True
    return False


# E712: Comparison to True should be 'if cond is True:' or 'if cond:'
def compare_to_true(value):
    if value == True:  # Should use 'if value:' or 'if value is True:'
        return "Value is true"


# F405: Name may be undefined, or defined from star imports
from math import *  # F403: 'from module import *' used
print(sin(90))  # Using sin without explicit import


# E713: Test for membership should be 'not in'
def test_membership(item, collection):
    if not item in collection:  # Should be 'if item not in collection:'
        return False
    return True


# E741: Do not use variables named 'l', 'O', or 'I'
def ambiguous_variable_names():
    l = 1  # Lowercase letter 'l' looks like number '1'
    O = 2  # Uppercase letter 'O' looks like number '0'
    I = 3  # Uppercase letter 'I' looks like number '1'
    return l + O + I


# Mixed tabs and spaces for indentation
def mixed_indentation():
    space_indent = "This line uses spaces"
	tab_indent = "This line uses a tab"  # E101, W191
    return space_indent + tab_indent
"""
    test_file.write_text(test_code)
    return code_dir


@pytest.fixture(scope="module")
def flake8_tool():
    """Initialize and configure Flake8Tool with test settings."""
    tool = FlakeTool()
    return tool


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_flake8_analysis(sample_code, flake8_tool):
    """Test full Flake8 analysis workflow from code scan to report generation."""
    try:
        # 1. Install the container image
        await flake8_tool.install()

        # 2. Run analysis on sample code
        results = await flake8_tool.run_scan(
            codebase_path=str(sample_code),
        )

        # 5. Validate summary
        assert results.summary["total"] == 1
        assert "by_severity" in results.summary

        assert "tool_name" in results.metadata
        assert "metrics" in results.metadata

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
