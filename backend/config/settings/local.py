import sys
from .base import *  # noqa
from .base import env

SECRET_KEY = env.str(
    "SECRET_KEY",
    default="!!!SET SECRET_KEY!!!",
)

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "verbose",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

if "test" in sys.argv or "test_coverage" in sys.argv:
    LOGGING = {}
