import os
import logging

logger = logging.getLogger(__name__)


class CredentialCodeBaseManager:

    def _init(self):
        self.ssh_key_path = None
        self.auth_token = None

    def configure_ssh(self, private_key_path: str = None):
        self.ssh_key_path = private_key_path
        if private_key_path:
            os.environ["GIT_SSH_COMMAND"] = f"ssh -i {private_key_path} -o StrictHostKeyChecking=no"
            logger.info(f"SSH credentials configured using with private key at {private_key_path}")

    def configure_token(self, token):
        self._auth_token = token
        logger.info("Authentication token configured")

    def get_auth_headers(self):
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
