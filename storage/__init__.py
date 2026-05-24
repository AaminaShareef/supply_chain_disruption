# storage/__init__.py
from .database   import init_db, get_session
from .repository import save_articles, get_alerts, get_stats

__all__ = ["init_db", "get_session", "save_articles", "get_alerts", "get_stats"]