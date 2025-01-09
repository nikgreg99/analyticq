import logging
from .dev_conf import DevConfig
from .prod_conf import ProdConfig
from .test_conf import TestConfig

logger = logging.getLogger(__name__)


def get_backend_config(env: str):
    logging.info(f"Loading config for {env} profle...")
    if env == "prod":
        return ProdConfig()
    elif env == "test":
        return TestConfig()
    return DevConfig()
