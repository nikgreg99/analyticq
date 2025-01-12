import json
import os
from pathlib import Path

import pytest
from analyticq.config import AnalyticQBaseConfig

TEST_DIR = os.path.dirname(__file__)
TEST_FILES_DIR = os.path.join(TEST_DIR, "test_files")


@pytest.fixture
def setup_environment():
    os.environ["SECRET_KEY_TEST"] = "test_env_secret_key"
    yield
    del os.environ["SECRET_KEY_TEST"]


def test_load_json_config(monkeypatch):
    monkeypatch.setattr(
        "analyticq.utils.get_backend_default_test_path",
        lambda: TEST_FILES_DIR
    )
    config = AnalyticQBaseConfig.load_config_file(Path(TEST_FILES_DIR), "test_config.json")
    assert config["dev"]["app_name"] == "AnalyticqDev"


def test_load_yaml_config(monkeypatch):
    monkeypatch.setattr(
        "analyticq.utils.get_backend_default_test_path",
        lambda: TEST_FILES_DIR
    )
    config = AnalyticQBaseConfig.load_config_file(Path(TEST_FILES_DIR), "test_config.yml")
    assert config["dev"]["host"] == "127.0.0.1"


@pytest.mark.skip(reason="Skipping this test for not running in CI/CD")
def test_from_file_default_config(monkeypatch):
    monkeypatch.setattr(
        "analyticq.utils.get_backend_default_config_path",
        lambda: TEST_FILES_DIR
    )
    monkeypatch.setattr(
        "analyticq.utils.get_default_analyticq_config_filename",
        lambda: "test_config.json"
    )
    config = AnalyticQBaseConfig.from_file(profile="dev")
    assert config.host == "127.0.0.1"


@pytest.mark.skip(reason="Skipping this test for not running in CI/CD")
def test_from_file_with_env_override(setup_environment, monkeypatch):
    monkeypatch.setattr(
        "analyticq.utils.get_backend_default_config_path",
        lambda: TEST_FILES_DIR
    )
    config = AnalyticQBaseConfig.from_file(profile="test")
    assert config.secret_key == "test_env_secret_key"
    assert config.app_name == "AnalyticQ-Backend"


def test_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        AnalyticQBaseConfig.load_config_file(Path(TEST_FILES_DIR), "test_config.txt")


def test_missing_profile(monkeypatch):
    monkeypatch.setattr(
        "analyticq.utils.get_config_analyticq_path",
        lambda: TEST_FILES_DIR
    )
    config = AnalyticQBaseConfig.from_file(conf_filename="test_config.json", profile="missing_profile")
    assert config is None


def test_save_to_json(monkeypatch, tmpdir):
    """Test saving configuration to a JSON file."""
    config_data = {
        "test": {
            "app_name": "TestApp",
            "debug": False,
            "host": "localhost",
            "port": 8080,
            "workers": 4,
        }
    }
    save_path = tmpdir.join("saved_config.json")
    AnalyticQBaseConfig.save_to_json(str(save_path), config_data)
    with open(save_path, "r") as f:
        saved_data = json.load(f)
    assert saved_data["test"]["app_name"] == "TestApp"
