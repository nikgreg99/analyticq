import pytest
from analyticq.engine.core.models import AnalyticQSASTScanResult
from analyticq.engine.tools.c import CppCheckTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def cppcheck_tool():
    """Initialize and configure CppcheckTool with test settings."""
    tool = CppCheckTool()
    return tool


@pytest.fixture(scope="module")
def sample_code(tmp_path_factory):
    """Create a temporary C++ file with known Cppcheck violations."""
    code_dir = tmp_path_factory.mktemp("code")
    test_file = code_dir / "test_sample.cpp"

    test_code = """#include <iostream>
#include <vector>
#include <memory>

class Resource {
    int* ptr;
public:
    Resource() {
        ptr = new int(42);  // Memory leak: no destructor
    }
};

void uninitializedVariable() {
    int x;
    std::cout << x;  // Uninitialized variable
}

void arrayOutOfBounds() {
    int arr[5];
    arr[5] = 0;  // Array index out of bounds
}

void nullPointerDeref() {
    int* ptr = nullptr;
    *ptr = 42;  // Null pointer dereference
}

void resourceLeak() {
    int* ptr = new int(42);
    // Missing delete: resource leak
}

void useAfterFree() {
    int* ptr = new int(42);
    delete ptr;
    *ptr = 0;  // Use after free
}

void divByZero(int x) {
    int result = 10 / x;  // Potential division by zero
}

class Base {
public:
    virtual void foo() {}
    // Missing virtual destructor
    ~Base() {}
};

class Derived : public Base {
public:
    void foo() override {}
};

void bufferOverflow() {
    char buffer[10];
    strcpy(buffer, "This string is too long for the buffer");  // Buffer overflow
}

int uninitializedMember() {
    struct Point {
        int x;
        int y;
    } p;
    return p.x;  // Uninitialized member
}

void deadPointer() {
    int* p;
    {
        int x = 0;
        p = &x;
    }
    *p = 42;  // Dead pointer
}

std::vector<int> returnDanglingReference() {
    std::vector<int> vec{1, 2, 3};
    return std::move(vec);  // Unnecessary std::move
}

void redundantCode() {
    if (true) {
        return;
    }
    std::cout << "Unreachable code";  // Unreachable code
}

int main() {
    // Memory leaks
    Resource r;

    // Potential null pointer dereference
    std::shared_ptr<int> sp;
    if (sp) {
        std::cout << *sp;
    }

    return 0;
}"""

    test_file.write_text(test_code)
    return code_dir


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_cpp_analysis(sample_code, cppcheck_tool):
    """Test full Cppcheck analysis workflow from code scan to report generation."""
    try:
        # 1. Install the container image
        await cppcheck_tool.install()

        # 2. Run analysis on sample code
        result = await cppcheck_tool.run_scan(
            codebase_path=str(sample_code),
        )

        assert isinstance(result, AnalyticQSASTScanResult)
        assert result.metadata["tool_name"] == "cppcheck"
        assert len(result.issues) > 0

        assert "metrics" in result.metadata

        for issue in result.issues:
            assert issue.path.endswith("test_sample.cpp")

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
