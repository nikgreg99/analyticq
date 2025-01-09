from .base_conf import BaseConfig


class ProdConfig(BaseConfig):
    debug: bool = False
    secret_key: str = "prod_key"
    workers: int = 4
    host: str = "0.0.0.0"  # Production IP
    port: int = 8081  # Production port
