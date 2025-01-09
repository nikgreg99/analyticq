from .base_conf import BaseConfig


class TestConfig(BaseConfig):
    debug: bool = True
    secret_key: str = "test_key"
