# flask_app/services/risk_analyser.py
# Runs the full analysis pipeline for a manufacturer search.
# Connects material finder → news fetcher → cleaning →
# classification → risk scoring → country extraction

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from processing.cleaner         import clean_article
from processing.language_filter import filter_english
from processing.merger          import weighted_merge
from processing.deduplicator    import deduplicate
from modelling.domain_classifier import classify_article
from modelling.risk_scorer       import calculate_risk_score
from .country_extractor          import extract_countries_from_all


def analyse_manufacturer(manufacturer: str, materials: list) -> dict:
    """
    Full analysis pipeline for a manufacturer.
    Returns a structured result with:
      - articles per material
      - risk per material
      - overall risk
      - filters data (countries, domains, risk levels)
    """
    from .news_fetcher import fetch_all_materials

    print(f"\n[risk_analyser] Analysing: {manufacturer}")
    print(f"[risk_analyser] Materials : {materials}")

    # Step 1 — Fetch news for all materials
    articles = fetch_all_materials(materials, manufacturer)

    if not articles:
        return {
            'manufacturer': manufacturer,
            'materials':    materials,
            'articles':     [],
            'stats':        {},
            'error':        'No articles found'
        }

    # Step 2 — Clean text
    articles = [clean_article(a) for a in articles]

    # Step 3 — Filter English
    articles = filter_english(articles)

    # Step 4 — Weighted merge and deduplicate
    articles = weighted_merge(articles)
    articles = deduplicate(articles)

    # Step 5 — Classify into domains
    articles = [classify_article(a) for a in articles]

    # Step 6 — Calculate risk scores
    articles = [calculate_risk_score(a) for a in articles]

    # Step 7 — Extract countries
    articles = extract_countries_from_all(articles)

    # Step 8 — Filter out unrelated articles
    articles = [a for a in articles if a.get('domains')]

    # Step 9 — Sort by risk score
    articles.sort(key=lambda a: a['risk_score'], reverse=True)

    # Step 10 — Build stats per material
    material_stats = {}
    for material in materials:
        mat_articles = [a for a in articles if a.get('material') == material]
        if mat_articles:
            avg_risk = sum(a['risk_score'] for a in mat_articles) / len(mat_articles)
            max_risk = max(a['risk_score'] for a in mat_articles)
            material_stats[material] = {
                'count':    len(mat_articles),
                'avg_risk': round(avg_risk, 2),
                'max_risk': round(max_risk, 2),
                'level':    get_risk_level(max_risk),
            }

    # Step 11 — Overall stats
    all_countries = sorted(set(
        c for a in articles for c in a.get('countries', [])
    ))
    all_domains = sorted(set(
        d for a in articles for d in a.get('domains', [])
    ))

    critical = [a for a in articles if a.get('risk_level') == 'critical']
    high     = [a for a in articles if a.get('risk_level') == 'high']
    medium   = [a for a in articles if a.get('risk_level') == 'medium']
    low      = [a for a in articles if a.get('risk_level') == 'low']

    overall_risk = 0
    if articles:
        overall_risk = round(
            sum(a['risk_score'] for a in articles) / len(articles), 2
        )

    print(f"[risk_analyser] Done! {len(articles)} relevant articles")
    print(f"[risk_analyser] Overall risk score: {overall_risk}")

    return {
        'manufacturer':   manufacturer,
        'materials':      materials,
        'overall_risk':   overall_risk,
        'overall_level':  get_risk_level(overall_risk),
        'material_stats': material_stats,
        'articles':       [format_article(a) for a in articles],
        'stats': {
            'total':    len(articles),
            'critical': len(critical),
            'high':     len(high),
            'medium':   len(medium),
            'low':      len(low),
        },
        'filters': {
            'countries': all_countries,
            'domains':   all_domains,
            'levels':    ['critical', 'high', 'medium', 'low'],
        }
    }


def get_risk_level(score: float) -> str:
    if score >= 70:   return 'critical'
    if score >= 50:   return 'high'
    if score >= 30:   return 'medium'
    return 'low'


def format_article(a: dict) -> dict:
    """Formats article for JSON response to frontend."""
    return {
        'title':      a.get('title_clean') or a.get('title', ''),
        'source':     a.get('source', ''),
        'url':        a.get('url', ''),
        'published':  a.get('published', ''),
        'material':   a.get('material', ''),
        'domains':    a.get('domains', []),
        'risk_score': a.get('risk_score', 0),
        'risk_level': a.get('risk_level', 'low'),
        'countries':  a.get('countries', []),
        'is_trusted': a.get('is_trusted', False),
    }