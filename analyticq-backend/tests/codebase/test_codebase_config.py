from analyticq.codebase.conf import ConfigCodebaseManager


def test_load__default_config():
    codebase_manager = ConfigCodebaseManager()
    default_config = codebase_manager._load_config()
    assert default_config["retention_days"] == 15
    assert default_config["default_branch"] == "main"
