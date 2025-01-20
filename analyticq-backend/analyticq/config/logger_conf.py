from logging.config import dictConfig

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        "console": {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}


def logging_init():
    dictConfig(LOGGING_CONFIG)
