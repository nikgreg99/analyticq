import json

from analyticq.util import AnalyticQConst, FileUtil


def test_get_default_AnalyticQ_config_filename():

    # Default case
    assert FileUtil.get_default_AnalyticQ_config_filename() == 'analyticq_backend_config.json'

    # Test with JSON extension
    assert FileUtil.get_default_AnalyticQ_config_filename(AnalyticQConst.JSON_EXTENSION) == 'analyticq_backend_config.json'

    # Test with YAML extension
    assert FileUtil.get_default_AnalyticQ_config_filename(AnalyticQConst.YAML_EXTENSION) == 'analyticq_backend_config.yaml'

    # Test with YML extension (fallback)
    assert FileUtil.get_default_AnalyticQ_config_filename(AnalyticQConst.YML_EXTENSION) == 'analyticq_backend_config.yml'

    # Test with an unsupported extension (should fallback to YML)
    assert FileUtil.get_default_AnalyticQ_config_filename('unsupported') == 'analyticq_backend_config.yml'


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
    FileUtil.save_to_json(save_path, config_data)
    with open(save_path, "r") as f:
        saved_data = json.load(f)
    assert saved_data["test"]["app_name"] == "TestApp"
