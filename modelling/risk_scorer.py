# modelling/risk_scorer.py
# Calculates a final risk score for each article based on:
#   1. Domain confidence scores from the classifier
#   2. Article quality score from the merger
#   3. Recency of the article
#   4. Source trustworthiness
#
# Final risk score is between 0 and 100.

from datetime import datetime, timezone
import re


def parse_date(date_str: str) -> datetime:
    """
    Tries to parse various date formats into a datetime object.
    Returns epoch if parsing fails.
    """
    if not date_str:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

    # Handle relative dates e.g. "2 hours ago"
    relative = re.match(r'(\d+)\s+(minute|hour|day|week)s?\s+ago', date_str.lower())
    if relative:
        amount, unit = int(relative.group(1)), relative.group(2)
        now = datetime.now(timezone.utc)
        if unit == 'minute': return now.replace(minute=now.minute - amount)
        if unit == 'hour':   return now.replace(hour=now.hour   - amount)
        if unit == 'day':    return now.replace(day=now.day     - amount)
        if unit == 'week':   return now.replace(day=now.day     - amount * 7)

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


def recency_multiplier(date_str: str) -> float:
    """
    Returns a multiplier based on how recent the article is.
      - Within 24 hours : 1.0  (full score)
      - Within 48 hours : 0.85
      - Within a week   : 0.70
      - Within a month  : 0.50
      - Older           : 0.30
    """
    dt  = parse_date(date_str)
    now = datetime.now(timezone.utc)

    try:
        age_hours = (now - dt).total_seconds() / 3600
    except Exception:
        return 0.30

    if age_hours <= 24:  return 1.00
    if age_hours <= 48:  return 0.85
    if age_hours <= 168: return 0.70
    if age_hours <= 720: return 0.50
    return 0.30


def calculate_risk_score(article: dict) -> dict:
    """
    Calculates a final risk score between 0 and 100 for an article.

    Formula:
      base_score     = average of matched domain confidence scores * 100
      quality_boost  = article quality score / 10  (max +7)
      recency        = base_score * recency_multiplier
      trust_boost    = +10 if from trusted source
      final          = capped at 100
    """
    domain_scores  = article.get('domain_scores', {})
    matched        = article.get('domains', [])

    if not matched:
        article['risk_score']  = 0.0
        article['risk_level']  = 'none'
        return article

    # 1. Base score from domain confidence
    avg_confidence = sum(domain_scores[d] for d in matched) / len(matched)
    base_score     = avg_confidence * 100

    # 2. Quality boost from merger score (max +7)
    quality_score  = article.get('quality_score', 0)
    quality_boost  = min(quality_score / 10, 7)

    # 3. Apply recency multiplier
    recency        = recency_multiplier(article.get('published', ''))
    score          = (base_score + quality_boost) * recency

    # 4. Trust boost
    if article.get('is_trusted'):
        score += 10

    # 5. Cap at 100
    final_score = round(min(score, 100), 2)

    # 6. Assign risk level
    if final_score >= 70:   risk_level = 'critical'
    elif final_score >= 50: risk_level = 'high'
    elif final_score >= 30: risk_level = 'medium'
    else:                   risk_level = 'low'

    article['risk_score'] = final_score
    article['risk_level'] = risk_level

    return article