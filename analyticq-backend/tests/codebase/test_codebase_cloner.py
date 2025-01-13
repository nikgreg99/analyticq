from pathlib import Path
from unittest.mock import patch

import pytest
from analyticq.codebase import CodebaseCloner, CodebaseProtocolType
from analyticq.utils import get_codebase_scripts_folder_path


@pytest.fixture
def codebase_cloner():
    with patch('analyticq.config.AnalyticQBaseConfig.get') as mock_config:
        mock_config.return_value = {"default_branch": "main"}
        return CodebaseCloner()


@pytest.mark.asyncio
async def test_clone_local_script_success(codebase_cloner):
    script_path = Path("/source/script.py")
    expected_dest_path = get_codebase_scripts_folder_path()

    with patch('analyticq.utils.get_codebase_scripts_folder_path') as mock_path, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('shutil.copy') as mock_copy:

        # Return the actual path that the code is using
        mock_path.return_value = expected_dest_path
        mock_exists.side_effect = [True, False]  # Source exists, destination doesn't

        await codebase_cloner.clone_local_script(script_path)
        # Assert with the exact path that's being used in the code
        mock_copy.assert_called_once_with(script_path, expected_dest_path / "scripts")


def test_get_protocol(codebase_cloner):
    assert codebase_cloner._get_protocol("git@github.com:user/repo.git") == CodebaseProtocolType.SSH
    assert codebase_cloner._get_protocol("https://github.com/user/repo.git") == CodebaseProtocolType.HTTPS
    assert codebase_cloner._get_protocol("http://github.com/user/repo.git") == CodebaseProtocolType.HTTP
