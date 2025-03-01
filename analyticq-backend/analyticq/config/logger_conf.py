from logging.config import dictConfig

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        "detailled": {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
        }
    },
    'handlers': {
        "console": {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'analyticq-backend.log',
            'formatter': 'detailed',
            'level': 'INFO',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}


def logging_init():
    dictConfig(LOGGING_CONFIG)
