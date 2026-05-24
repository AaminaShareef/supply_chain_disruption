# storage/repository.py
# Handles all read and write operations to the database.
# All other modules use this file to interact with the database —
# they never write SQL directly.

from sqlalchemy.exc import IntegrityError
from .database import get_session
from .models   import DisruptionEvent


def save_articles(articles: list) -> dict:
    """
    Saves a list of classified articles to the database.
    Skips duplicates (same URL) silently.
    Returns a summary of what was saved.
    """
    session   = get_session()
    saved     = 0
    skipped   = 0

    try:
        for a in articles:
            event = DisruptionEvent(
                url           = a.get('url',           ''),
                title         = a.get('title',         ''),
                title_clean   = a.get('title_clean',   ''),
                body          = a.get('body',          ''),
                body_clean    = a.get('body_clean',    ''),
                source        = a.get('source',        ''),
                published     = a.get('published',     ''),
                domain_hint   = a.get('domain_hint',   ''),
                domains       = a.get('domains',       []),
                domain_scores = a.get('domain_scores', {}),
                risk_score    = a.get('risk_score',    0.0),
                risk_level    = a.get('risk_level',    'low'),
                quality_score = a.get('quality_score', 0.0),
                is_trusted    = a.get('is_trusted',    False),
            )

            try:
                session.add(event)
                session.commit()
                saved += 1
            except IntegrityError:
                session.rollback()
                skipped += 1

    finally:
        session.close()

    print(f"[repository] Saved {saved} new articles, skipped {skipped} duplicates")
    return {'saved': saved, 'skipped': skipped}


def get_alerts(risk_level: str = None, limit: int = 50) -> list:
    """
    Fetches disruption alerts from the database.
    Optionally filter by risk level: critical, high, medium, low
    Returns a list of dicts sorted by risk score descending.
    """
    session = get_session()

    try:
        query = session.query(DisruptionEvent)

        if risk_level:
            query = query.filter(DisruptionEvent.risk_level == risk_level)

        query = query.order_by(DisruptionEvent.risk_score.desc()).limit(limit)
        events = query.all()

        return [
            {
                'id':           e.id,
                'title':        e.title_clean or e.title,
                'source':       e.source,
                'url':          e.url,
                'domains':      e.domains,
                'risk_score':   e.risk_score,
                'risk_level':   e.risk_level,
                'published':    e.published,
                'created_at':   str(e.created_at),
            }
            for e in events
        ]

    finally:
        session.close()


def get_stats() -> dict:
    """
    Returns a summary of all disruption events in the database.
    """
    session = get_session()

    try:
        total    = session.query(DisruptionEvent).count()
        critical = session.query(DisruptionEvent).filter_by(risk_level='critical').count()
        high     = session.query(DisruptionEvent).filter_by(risk_level='high').count()
        medium   = session.query(DisruptionEvent).filter_by(risk_level='medium').count()
        low      = session.query(DisruptionEvent).filter_by(risk_level='low').count()

        return {
            'total':    total,
            'critical': critical,
            'high':     high,
            'medium':   medium,
            'low':      low,
        }

    finally:
        session.close()