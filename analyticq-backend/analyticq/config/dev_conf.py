from .base_conf import BaseConfig


class DevConfig(BaseConfig):
    debug: bool = True
    secret_key: str = "dev_key"
