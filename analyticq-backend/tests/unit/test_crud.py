import os
from pathlib import Path

import pytest
from analyticq.config import AnalyticQBaseConfig, AnalyticQEnvironmentLoader
from analyticq.manager.db_manager import AnalyticQDatabaseManager
from analyticq.model import AnalyticQSASTScanResult

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent


@pytest.fixture(autouse=True)
async def setup_db():
    """
    Set up the database schema before each test and tear it down afterward.
    """
    # Use absolute paths based on the project structure
    test_file = BASE_DIR / "unit" / "test_files"
    print(f"Config directory path: {test_file}")
    AnalyticQBaseConfig.load_config_file(str(test_file), "test_config.json")

    test_env_file = BASE_DIR / "unit" / "test_files" / ".env.test"
    print(f"Environment file path: {test_env_file}")

    AnalyticQEnvironmentLoader.load(test_env_file, "test")
    db_manager = AnalyticQDatabaseManager()
    await db_manager.init_db()
    yield
    await db_manager.close()


@pytest.mark.asyncio
async def test_add_scan_result(setup_db):
    # Add a new scan result
    scan_result_data = {
        "scan_id": "SCAN123",
        "summary": {"total_issues": 1, "critical_issues": 0},
        "scan_metadata": {"tool_version": "1.0.0"}
    }
    await AnalyticQSASTScanResult.add(scan_result_data)

    # Retrieve the scan result
    scan_result = await AnalyticQSASTScanResult.get_by_scan_id("SCAN123")
    assert scan_result is not None
    assert scan_result.scan_id == "SCAN123"
    assert scan_result.summary == {"total_issues": 1, "critical_issues": 0}


@pytest.mark.asyncio
async def test_get_scan_result_by_id(setup_db):
    scan_id = "SCAN123"
    expected_scan_result_data = {
        "scan_id": "SCAN123",
        "summary": {"total_issues": 1, "critical_issues": 0},
        "scan_metadata": {"tool_version": "1.0.0"}
    }
    await AnalyticQSASTScanResult.add(expected_scan_result_data)

    scan_result = await AnalyticQSASTScanResult.get_by_scan_id(scan_id)

    assert scan_result is not None
    assert scan_result.scan_id == expected_scan_result_data["scan_id"], f"Expected {expected_scan_result_data["scan_id"]}, got {scan_result.scan_id}"
    assert scan_result.summary == expected_scan_result_data["summary"], f"Expected {expected_scan_result_data["summary"]}, got {scan_result.summary}"


@pytest.mark.asyncio
async def test_update_scan_result_by_id(setup_db):
    scan_id = "SCAN123"
    expected_scan_result_data = {
        "scan_id": "SCAN123",
        "summary": {"total_issues": 1, "critical_issues": 0},
        "scan_metadata": {"tool_version": "1.0.0"}
    }
    await AnalyticQSASTScanResult.add(expected_scan_result_data)

    updated_scan_result_data = {
        "summary": {"total_issues": 1, "critical_issues": 2},
        "scan_metadata": {"tool_version": "2.0.0"}
    }

    await AnalyticQSASTScanResult.update_by_scan_id(scan_id, **updated_scan_result_data)

    updated_record = await AnalyticQSASTScanResult.get_by_scan_id(scan_id)
    assert updated_record.summary["critical_issues"] == 2
    assert updated_record.scan_metadata["tool_version"] == "2.0.0"


@pytest.mark.asyncio
async def test_get_scan_issues_by_id_empty(setup_db):
    scan_id = "SCAN123"
    expected_scan_result_data = {
        "scan_id": "SCAN123",
        "summary": {"total_issues": 1, "critical_issues": 0},
        "scan_metadata": {"tool_version": "1.0.0"}
    }
    await AnalyticQSASTScanResult.add(expected_scan_result_data)

    scan_issues = await AnalyticQSASTScanResult.get_all_issues_by_scan_id(scan_id)

    len(scan_issues) == 0, "Expected list to be empty"


@pytest.mark.asyncio
async def test_delete_scan_by_id(setup_db):
    scan_id = "SCAN123"
    expected_scan_result_data = {
        "scan_id": "SCAN123",
        "summary": {"total_issues": 1, "critical_issues": 0},
        "scan_metadata": {"tool_version": "1.0.0"}
    }
    await AnalyticQSASTScanResult.add(expected_scan_result_data)

    scan_result = await AnalyticQSASTScanResult.delete_by_scan_id(scan_id)

    assert scan_result is None, "Expected None"
