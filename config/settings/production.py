from .base import *  # noqa
from .base import env

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = [".herokuapp.com"]
