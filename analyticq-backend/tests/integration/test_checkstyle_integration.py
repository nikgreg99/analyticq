import os

import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.engine.tools import CheckstyleTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def checkstyle_tool():
    """Initialize and configure CheckstyleTool with test settings."""
    tool = CheckstyleTool()
    # Reduce timeout for test environment
    return tool


@pytest.fixture(scope="module")
def sample_java_app(tmp_path_factory):
    """Create a temporary Java application structure with known style violations."""
    app_dir = tmp_path_factory.mktemp("java_app")

    # Create basic Java app structure
    create_java_directory_structure(app_dir)

    # Create source file with style violations
    src_dir = app_dir / "src" / "main" / "java" / "com" / "example" / "app"
    main_class = src_dir / "App.java"

    main_code = """
package com.example.app;

import java.util.*;
import java.io.*;

public class App {
    // Missing Javadoc
    public static void main(String[] args) {
        // Line longer than 100 characters
        System.out.println("This is a very long line that exceeds the recommended maximum length of 100 characters for readability purposes.");

        // Incorrect indentation
       System.out.println("Incorrect indentation");

        // Unused imports

        // Magic number
        for (int i = 0; i < 42; i++) {
            System.out.println(i);
        }

        // Missing spaces around operators
        int x=5+3;


        // Non-final static variable
        static String NON_FINAL_CONSTANT = "should be final";

        // Missing braces
        if (true)
            System.out.println("Missing braces");

        // Trailing whitespace
        System.out.println("Trailing spaces");

    }

    // Too many parameters
    public void tooManyParams(int a, int b, int c, int d, int e, int f, int g, int h) {
        return;
    }

}
"""
    main_class.write_text(main_code)

    # Create another class with different style violations
    util_class = src_dir / "Util.java"

    util_code = """
package com.example.app;

// Improper class name (should start with uppercase)
class Util {
    // Variable name doesn't follow convention
    private int BAD_variable_Name;

    // Method name doesn't follow convention
    public void Bad_Method_Name() {
        return;
    }

    // Nested blocks
    public void nestedBlocks() {
        {
            {
                {
                    System.out.println("Too many nested blocks");
                }
            }
        }
    }

    // Hidden field
    public void hiddenField(int BAD_variable_Name) {
        this.BAD_variable_Name = BAD_variable_Name;
    }
}
"""
    util_class.write_text(util_code)

    return app_dir


def create_java_directory_structure(app_dir):
    """Create the basic Java app directory structure."""
    directories = [
        "src/main/java/com/example/app",
        "src/test/java/com/example/app",
    ]

    for directory in directories:
        os.makedirs(app_dir / directory, exist_ok=True)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_checkstyle_analysis(checkstyle_tool, sample_java_app):
    try:
        # 1. Install the tool
        await checkstyle_tool.install()

        # 2. Run analysis on sample Java app
        results = await checkstyle_tool.run_scan(
            codebase_path=str(sample_java_app)
        )
        print(results)

        assert isinstance(results, AnalyticQSASTScanResultModel), "Invalid results type"
        assert len(results.issues) > 1, "Should find at least one issue"

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssueModel), "Invalid issue type"
            assert issue.rule_id is not None
            assert issue.path is not None
            assert issue.message is not None
            assert issue.severity is not AnalyticQSeverity.UNKNOWN
            assert issue.confidence is AnalyticQConfidence.UNKNOWN

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
