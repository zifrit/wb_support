import os

from backend.app.core.config import get_settings


os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DEBUG", "false")
get_settings.cache_clear()
