import os
import shutil
from pathlib import Path

import pytest
from analyticq.config import AnalyticQBaseConfig
from analyticq.util import PathUtil

TEST_DIR = Path(os.path.dirname(__file__)).parent
TEST_FILES_DIR = os.path.join(str(TEST_DIR), "test_files")


@pytest.fixture
def setup_environment():
    os.environ["SECRET_KEY_TEST"] = "test_env_secret_key"
    yield
    del os.environ["SECRET_KEY_TEST"]


@pytest.fixture(autouse=True)
def mock_config_data():
    # Simulate loading settings by manually setting the config data
    config_data = {
        "app_name": "AnalyticQ-Backend",
        "debug": True,
        "host": "127.0.0.1",
        "port": 5000,
        "workers": 1,
        "secret_key": "testsecret"
    }
    AnalyticQBaseConfig.settings = config_data
    yield config_data  # The fixture returns config_data


def test_load_json_config(monkeypatch):
    monkeypatch.setattr(
        "analyticq.util.PathUtil.get_backend_default_test_AnalyticQ_path",
        lambda: TEST_FILES_DIR
    )
    config = AnalyticQBaseConfig.load_config_file(Path(TEST_FILES_DIR), "test_config.json")
    assert config["dev"]["app_name"] == "AnalyticQDev"


def test_load_yaml_config(monkeypatch):
    monkeypatch.setattr(
        "analyticq.util.PathUtil.get_backend_default_test_AnalyticQ_path",
        lambda: TEST_FILES_DIR
    )
    config = AnalyticQBaseConfig.load_config_file(Path(TEST_FILES_DIR), "test_config.yml")
    assert config["dev"]["host"] == "127.0.0.1"


@pytest.mark.skip(reason="Skipping this test for not running in CI/CD")
def test_from_file_default_config(monkeypatch):
    monkeypatch.setattr(
        "analyticq.util.PathUtil.get_backend_default_config_AnalyticQ_path",
        lambda: TEST_FILES_DIR
    )
    monkeypatch.setattr(
        "analyticq.util.FileUtil.get_default_AnalyticQ_config_filename",
        lambda: "test_config.json"
    )
    config = AnalyticQBaseConfig.from_file(profile="dev")
    assert config.host == "127.0.0.1"


@pytest.mark.skip(reason="Skipping this test for not running in CI/CD")
def test_from_file_with_env_override(setup_environment, monkeypatch):
    monkeypatch.setattr(
        "analyticq.util.PathUtil.get_backend_default_config_AnalyticQ_path",
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
        "analyticq.util.PathUtil",
        lambda: TEST_FILES_DIR
    )
    config = AnalyticQBaseConfig.from_file(conf_filename="test_config.json", profile="missing_profile")
    assert config is None


def test_get_with_initialized_settings():
    # Retrieve a setting using the static `get` method
    app_name = AnalyticQBaseConfig.get("app_name")

    # Assert that the value is correct
    assert app_name == "AnalyticQ-Backend"


def test_get_without_initialized_settings():
    if hasattr(AnalyticQBaseConfig, 'settings'):
        delattr(AnalyticQBaseConfig, 'settings')

    result = AnalyticQBaseConfig.get("app_name", "default_value")

    assert result == "default_value"


def test_empty_config_file_cleanup():

    cwd = PathUtil.get_current_cwd_path()
    temp_dir = cwd / "temp_test_dir"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Percorso del file di configurazione vuoto
        empty_config_path = temp_dir / "empty_config.json"

        # Creazione del file vuoto
        with open(empty_config_path, "w") as f:
            f.write("")  # Scrive un file vuoto

        with pytest.raises(ValueError):
            AnalyticQBaseConfig.load_config_file(temp_dir, "empty_config.json")
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
