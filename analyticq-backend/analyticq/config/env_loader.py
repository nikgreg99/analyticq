import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class AnalyticQEnvironmentLoader:
    """
    A class to load environment variables from profile-specific .env files.
    """
    @staticmethod
    def load(conf_path_env: str, profile: str) -> None:
        """
        Load environment variables from a profile-specific .env file.

        Args:
            profile: The profile name (e.g., "dev", "prod") to load the environment file for.
        """
        if os.path.exists(conf_path_env):
            load_dotenv(conf_path_env, override=True)
            logger.info(f"Loaded {profile} profile...")
        else:
            logger.warning(f".env file for profile {profile} was not found at: {conf_path_env}")
