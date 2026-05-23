# processing/merger.py
# Scores and ranks articles from all sources before deduplication.
# This ensures we keep the BEST version of each story, not just the first.
#
# Scoring weights:
#   - Trusted source      : +40 points
#   - Source priority     : up to +30 points
#   - Recency             : up to +20 points
#   - Has body text       : +10 points

from datetime import datetime, timezone
import re

# --- Source priority ranking (higher = better) ---
SOURCE_PRIORITY = {
    # Tier 1 — Premium wire services
    'reuters':          30,
    'associated press': 30,
    'ap news':          30,
    'bloomberg':        28,
    'financial times':  28,
    'wsj':              28,
    'wall street journal': 28,

    # Tier 2 — Major broadcasters
    'bbc':              25,
    'cnbc':             25,
    'cnn':              22,
    'al jazeera':       22,
    'aljazeera':        22,
    'the guardian':     22,
    'guardian':         22,
    'forbes':           20,

    # Tier 3 — Supply chain specialists
    'supply chain dive':   18,
    'supplychaindive':     18,
    'supply chain brain':  18,
    'supplychainbrain':    18,
    'logistics management':15,
    'logisticsmgmt':       15,

    # Tier 4 — General news
    'who':              15,
    'fema':             15,
    'yahoo news':       10,
    'google news':      10,
}


def parse_date(date_str: str) -> datetime:
    """
    Tries to parse various date formats into a datetime object.
    Returns epoch (oldest possible) if parsing fails.
    """
    if not date_str:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

    # Handle relative dates from SerpAPI e.g. "2 hours ago", "3 days ago"
    relative = re.match(r'(\d+)\s+(minute|hour|day|week)s?\s+ago', date_str.lower())
    if relative:
        amount, unit = int(relative.group(1)), relative.group(2)
        now = datetime.now(timezone.utc)
        if unit == 'minute': return now.replace(minute=now.minute - amount)
        if unit == 'hour':   return now.replace(hour=now.hour - amount)
        if unit == 'day':    return now.replace(day=now.day - amount)
        if unit == 'week':   return now.replace(day=now.day - amount * 7)

    # Try common date formats
    formats = [
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S%z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S %z',
        '%B %d, %Y',
        '%b %d, %Y',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def recency_score(date_str: str) -> float:
    """
    Returns a score between 0 and 20 based on how recent the article is.
      - Published today        : 20 points
      - Published yesterday    : 15 points
      - Published this week    : 10 points
      - Published this month   : 5  points
      - Older                  : 0  points
    """
    dt  = parse_date(date_str)
    now = datetime.now(timezone.utc)

    try:
        age_hours = (now - dt).total_seconds() / 3600
    except Exception:
        return 0

    if age_hours <= 24:   return 20
    if age_hours <= 48:   return 15
    if age_hours <= 168:  return 10   # within a week
    if age_hours <= 720:  return 5    # within a month
    return 0


def source_priority_score(source: str) -> float:
    """
    Returns a score between 0 and 30 based on source reputation.
    """
    source_lower = source.lower()
    for name, score in SOURCE_PRIORITY.items():
        if name in source_lower:
            return score
    return 5   # unknown source gets a small base score


def score_article(article: dict) -> float:
    """
    Calculates a total quality score for an article.
    Higher score = higher quality = kept during deduplication.
    """
    score = 0

    # 1. Trusted source flag (set by fetchers)
    if article.get('is_trusted'):
        score += 40

    # 2. Source priority
    score += source_priority_score(article.get('source', ''))

    # 3. Recency
    score += recency_score(article.get('published', ''))

    # 4. Has a meaningful body
    body = article.get('body_clean') or article.get('body', '')
    if len(body) > 50:
        score += 10

    return score


def weighted_merge(articles: list) -> list:
    """
    Scores every article and sorts them highest score first.
    Deduplication will then naturally keep the best version of each story.
    """
    for article in articles:
        article['quality_score'] = score_article(article)

    # Sort by quality score descending
    articles.sort(key=lambda a: a['quality_score'], reverse=True)

    print(f"[merger] {len(articles)} articles scored and ranked")
    print(f"[merger] Top score    : {articles[0]['quality_score']:.1f} — {articles[0].get('source','?')}")
    print(f"[merger] Bottom score : {articles[-1]['quality_score']:.1f} — {articles[-1].get('source','?')}")

    return articles