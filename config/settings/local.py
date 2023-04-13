from .base import *  # noqa
from .base import env

SECRET_KEY = env.str(
    "SECRET_KEY",
    default="!!!SET SECRET_KEY!!!",
)

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
