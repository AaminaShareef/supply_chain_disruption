# flask_app/services/country_extractor.py
# Extracts country mentions from article text.
# Used for the country filter on the dashboard.

import re

# --- Common countries and their variations ---
COUNTRY_PATTERNS = {
    'United States':    ['united states', 'usa', 'u.s.', 'america', 'washington'],
    'China':            ['china', 'chinese', 'beijing', 'shanghai'],
    'Russia':           ['russia', 'russian', 'moscow'],
    'India':            ['india', 'indian', 'new delhi', 'mumbai'],
    'Germany':          ['germany', 'german', 'berlin'],
    'United Kingdom':   ['united kingdom', 'uk', 'britain', 'british', 'london'],
    'France':           ['france', 'french', 'paris'],
    'Japan':            ['japan', 'japanese', 'tokyo'],
    'South Korea':      ['south korea', 'korean', 'seoul'],
    'Australia':        ['australia', 'australian', 'sydney', 'melbourne'],
    'Canada':           ['canada', 'canadian', 'toronto', 'ottawa'],
    'Brazil':           ['brazil', 'brazilian', 'sao paulo', 'brasilia'],
    'South Africa':     ['south africa', 'johannesburg', 'cape town'],
    'Mexico':           ['mexico', 'mexican', 'mexico city'],
    'Indonesia':        ['indonesia', 'indonesian', 'jakarta'],
    'Saudi Arabia':     ['saudi arabia', 'saudi', 'riyadh'],
    'UAE':              ['uae', 'dubai', 'abu dhabi', 'emirates'],
    'Turkey':           ['turkey', 'turkish', 'ankara', 'istanbul'],
    'Nigeria':          ['nigeria', 'nigerian', 'lagos', 'abuja'],
    'Congo':            ['congo', 'drc', 'kinshasa', 'democratic republic'],
    'Ukraine':          ['ukraine', 'ukrainian', 'kyiv', 'kiev'],
    'Chile':            ['chile', 'chilean', 'santiago'],
    'Peru':             ['peru', 'peruvian', 'lima'],
    'Zambia':           ['zambia', 'zambian', 'lusaka'],
    'Ghana':            ['ghana', 'ghanaian', 'accra'],
    'Kazakhstan':       ['kazakhstan', 'kazakh', 'astana'],
    'Philippines':      ['philippines', 'filipino', 'manila'],
    'Malaysia':         ['malaysia', 'malaysian', 'kuala lumpur'],
    'Thailand':         ['thailand', 'thai', 'bangkok'],
    'Vietnam':          ['vietnam', 'vietnamese', 'hanoi'],
    'Myanmar':          ['myanmar', 'burma', 'burmese', 'yangon'],
}


def extract_countries(text: str) -> list:
    """
    Extracts all country mentions from a piece of text.
    Returns a list of country names found.
    """
    if not text:
        return []

    text_lower  = text.lower()
    found       = []

    for country, patterns in COUNTRY_PATTERNS.items():
        if any(pattern in text_lower for pattern in patterns):
            found.append(country)

    return found


def extract_countries_from_article(article: dict) -> dict:
    """
    Extracts countries from article title and body.
    Adds 'countries' field to the article dict.
    """
    text = (
        (article.get('title_clean') or article.get('title', '')) + ' ' +
        (article.get('body_clean')  or article.get('body',  ''))
    )

    article['countries'] = extract_countries(text)
    return article


def extract_countries_from_all(articles: list) -> list:
    """
    Extracts countries from all articles.
    """
    return [extract_countries_from_article(a) for a in articles]