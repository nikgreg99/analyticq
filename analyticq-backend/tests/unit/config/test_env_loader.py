from unittest.mock import patch

from analyticq.config import AnalyticQEnvironmentLoader


@patch("os.path.exists", return_value=True)
@patch("dotenv.load_dotenv")
def test_load_environment_found(mock_exists, mock_load_dotenv):
    profile = "dev"
    conf_path_env = f".env.{profile}"

    # Simulate the .env file being found and loaded
    AnalyticQEnvironmentLoader.load(conf_path_env, profile)

    # Verify load_dotenv was called with the correct path
    mock_load_dotenv.exist(conf_path_env, profile)


@patch("os.path.exists", return_value=False)
@patch("dotenv.load_dotenv")
def test_load_environment_file_not_found(mock_load_dotenv, mock_exists):
    profile = "dev"
    conf_path_env = f".env.{profile}"

    AnalyticQEnvironmentLoader.load(conf_path_env, profile)

    mock_load_dotenv.assert_not_called()
