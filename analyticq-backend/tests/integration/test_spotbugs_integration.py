import pytest
from analyticq.engine.core.models import (AnalyticQConfidence,
                                          AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel,
                                          AnalyticQSeverity)
from analyticq.engine.tools import SpotBugTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def spotbugs_tool():
    "Initialize and configure StaticcheckTool with test settings."""
    tool = SpotBugTool()
    # Reduce timeout for test environment
    return tool


@pytest.fixture(scope="module")
def sample_java_code(tmp_path_factory):
    """Create a temporary Java file with known SpotBugs violations."""
    code_dir = tmp_path_factory.mktemp("code")

    # Create package structure
    package_dir = code_dir / "com" / "example"
    package_dir.mkdir(parents=True)

    test_file = package_dir / "TestSample.java"

    # Create a sample Java file with known SpotBugs issues
    test_code = """
package com.example;

import java.util.Arrays;
import java.util.Random;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class TestSample {
    // MS_SHOULD_BE_FINAL: Field isn't final but should be
    public static String CONSTANT = "This should be final";

    // UPM_UNCALLED_PRIVATE_METHOD: Private method is never called
    private void unusedMethod() {
        System.out.println("This method is never called");
    }

    // NP_NULL_ON_SOME_PATH: Possible null pointer dereference
    public String nullPointerIssue(String input) {
        String result = null;
        if (input.length() > 5) {
            result = "Long input";
        }
        // Potential null dereference if input length <= 5
        return result.toUpperCase();
    }

    // DLS_DEAD_LOCAL_STORE: Dead store to local variable
    public void deadStore() {
        int unused = 10;  // Value is never used
        System.out.println("Hello");
    }

    // RV_RETURN_VALUE_IGNORED: Return value of method is ignored
    public void ignoreReturnValue() {
        String data = "test,data";
        data.replace(",", ";");  // Return value is ignored
    }

    // EI_EXPOSE_REP: May expose internal representation by returning reference to mutable object
    private final byte[] secretData = new byte[10];
    public byte[] getSecretData() {
        return secretData;  // Should return a copy instead
    }
    // DMI_RANDOM_USED_ONLY_ONCE: Random object created and used only once
    public int singleUseRandom() {
        return new Random().nextInt();
    }

    // Thread safety issue
    private Integer counter = 0;
    public void threadIssue() {
        Executor executor = Executors.newFixedThreadPool(10);
        executor.execute(() -> counter++);  // Not thread-safe
    }
}
    """
    test_file.write_text(test_code)

    # Create a basic pom.xml file for Maven build
    pom_file = code_dir / "pom.xml"
    pom_content = """
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>test-sample</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
</project>
    """
    pom_file.write_text(pom_content)

    return code_dir


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_analysis(spotbugs_tool, sample_java_code):
    """Test full SpotBugs analysis workflow from code scan to report generation."""
    try:
        # 1. Install the container image
        await spotbugs_tool.install()

        # 2. Run analysis on sample code
        results = await spotbugs_tool.run_scan(
            codebase_path=str(sample_java_code),
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
