import logging
import os
from threading import Lock

logger = logging.getLogger(__name__)


class CredentialCodeBaseManager:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)

    def _init(self):
        self.ssh_key_path = None
        self.auth_token = None

    def configure_ssh(self, private_key_path: str = None):
        self.ssh_key_path = private_key_path
        if private_key_path:
            os.environ["GIT_SSH_COMMAND"] = f"ssh -i {private_key_path} -o StrictHostKeyChecking=no"
            logger.info(f"SSH credentials configured using with private key at {private_key_path}")
        else:
            os.environ.pop("GIT_SSH_COMMMAND", None)
            logger.warning("SSH confituatio ")

    def configure_token(self, token):
        self._auth_token = token
        logger.info("Authentication token configured")

    def get_auth_headers(self):
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    @property
    def ssh_key_path(self):
        return self.ssh_key_path

    @property
    def auth_token(self):
        return self._auth_token
