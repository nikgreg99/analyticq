import logging
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class AnalyticQEnvironmentLoader:
    """
    A class to load environment variables from profile-specific .env files.
    """
    @staticmethod
    def load(conf_path_env: str, profile: str, *, strict: bool = False) -> None:
        """
        Load environment variables from a profile-specific .env file.

        Args:
            profile: The profile name (e.g., "dev", "prod") to load the environment file for.
        """
        if not profile.strip():
            raise ValueError("Profile name cannot be empty or whitespace.")

        conf_path_env = Path(conf_path_env)

        if conf_path_env.exists():
            load_dotenv(dotenv_path=conf_path_env, override=True)
            logger.info(f"[{profile}] Environment loaded from: {conf_path_env.resolve()}")
            return True
        else:
            message = f"[{profile}] .env file not found at: {conf_path_env.resolve()}"
            if strict:
                raise FileNotFoundError(message)
            logger.warning(message)
            return False
