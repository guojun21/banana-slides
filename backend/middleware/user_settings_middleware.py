"""
User Settings Middleware

On each request, reads X-User-Token header, loads user settings
from database, and stores in g.user_settings for per-request access.

All config consumers use get_user_config() from utils.config_utils
to read g.user_settings with fallback to current_app.config defaults.
No global config mutation happens here.
"""
import logging
from flask import request, g
from models import Settings

logger = logging.getLogger(__name__)


def load_user_settings():
    """
    Before each request: load user settings into g.user_settings.
    """
    user_token = request.headers.get('X-User-Token')

    if user_token:
        try:
            settings = Settings.get_settings(user_token)
            g.user_settings = settings
            logger.debug(f"Loaded settings for user: {user_token[:8]}...")
        except Exception as e:
            logger.error(f"Failed to load user settings: {e}")
            g.user_settings = None
    else:
        g.user_settings = None
        logger.debug("No user token provided, using default settings")


def restore_default_settings(response):
    """No-op kept for backward compatibility with app.after_request registration."""
    return response
