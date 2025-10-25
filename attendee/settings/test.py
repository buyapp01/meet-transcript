import os

import dj_database_url

from .base import *

DEBUG = True
SITE_DOMAIN = "localhost:8000"
ALLOWED_HOSTS = []

# Use DATABASE_URL if set, otherwise fall back to local test database
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql://attendee_test_user:attendee_test_user@localhost:5432/attendee_test"
        ),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Log more stuff in development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
