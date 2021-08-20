import os
import sys

from environs import Env

env = Env()

DEBUG = True
SECRET_KEY = "thisisnotneeded"


MIDDLEWARE = []

SITE_ID = 1

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "sops",
    "projects",
    "gql",
    "backoffice",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"console": {"format": "%(asctime)s %(levelname)-8s %(name)-12s %(message)s"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "stream": sys.stdout,
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "hurricane": {
            "handlers": ["console"],
            "level": os.getenv("HURRICANE_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "pika": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("DATABASE_NAME"),
        "USER": env.str("DATABASE_USER"),
        "HOST": env.str("DATABASE_HOST"),
        "PORT": env.int("DATABASE_PORT", 5432),
    }
}

if env.str("DATABASE_PASSWORD", None):
    DATABASES["default"]["PASSWORD"] = env.str("DATABASE_PASSWORD")

AUTH_USER_MODEL = "backoffice.AdminUser"

GRAPHENE_PER_PAGE = 30

CELERY_TASK_ALWAYS_EAGER = True
