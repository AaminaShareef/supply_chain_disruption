# flask_app/services/news_fetcher.py
# Fetches real-time news for each raw material identified.
# Uses SerpAPI (Google News) and NewsAPI.

import requests
import os
from concurrent.futures import ThreadPoolExecutor


TRUSTED_SOURCES = [
    'reuters.com', 'apnews.com', 'bbc.com', 'bloomberg.com',
    'ft.com', 'wsj.com', 'cnbc.com', 'theguardian.com',
    'aljazeera.com', 'forbes.com', 'supplychaindive.com',
    'mining.com', 'metalsbulletin.com', 'commodityintelligence.com'
]

SPAM_KEYWORDS = [
    'giveaway', 'click here', 'win free', 'make money',
    'crypto', 'nft', 'discount', 'promo', 'buy now',
    'limited offer', 'sponsored', 'advertisement'
]


def get_source_name(source) -> str:
    if isinstance(source, dict):
        return source.get('name', '')
    if isinstance(source, str):
        return source
    return ''


def is_quality_article(article: dict) -> bool:
    title = (article.get('title') or '').lower()
    text  = title
    if len(title) < 15:
        return False
    if any(spam in text for spam in SPAM_KEYWORDS):
        return False
    return True


def fetch_serpapi_material(material: str, manufacturer: str) -> list:
    """Fetches Google News for a specific material + supply chain context."""
    api_key  = os.getenv('SERPAPI_KEY', '')
    articles = []

    if not api_key:
        return []

    # Search queries focused on supply disruption
    queries = [
        f"{material} supply disruption shortage",
        f"{material} supply chain risk {manufacturer}",
    ]

    for query in queries:
        try:
            resp = requests.get(
                'https://serpapi.com/search',
                params = {
                    'engine':  'google_news',
                    'q':       query,
                    'api_key': api_key,
                    'hl':      'en',
                    'gl':      'us',
                },
                timeout = 15
            )

            if resp.status_code != 200:
                continue

            for a in resp.json().get('news_results', []):
                if not is_quality_article(a):
                    continue

                link       = a.get('link', '')
                is_trusted = any(t in link.lower() for t in TRUSTED_SOURCES)

                articles.append({
                    'title':       a.get('title', ''),
                    'body':        a.get('snippet', ''),
                    'url':         link,
                    'source':      get_source_name(a.get('source', '')),
                    'published':   a.get('date', ''),
                    'material':    material,
                    'manufacturer':manufacturer,
                    'domain_hint': 'economic',
                    'is_trusted':  is_trusted,
                })

        except Exception as e:
            print(f"[news_fetcher] Error for '{query}': {e}")

    return articles


def fetch_newsapi_material(material: str, manufacturer: str) -> list:
    """Fetches NewsAPI articles for a specific material."""
    api_key  = os.getenv('NEWSAPI_KEY', '')
    articles = []

    if not api_key:
        return []

    try:
        resp = requests.get(
            'https://newsapi.org/v2/everything',
            params = {
                'q':        f"{material} supply shortage disruption",
                'language': 'en',
                'sortBy':   'publishedAt',
                'pageSize': 10,
                'apiKey':   api_key,
            },
            timeout = 10
        )

        if resp.status_code == 200:
            for a in resp.json().get('articles', []):
                if not is_quality_article(a):
                    continue

                articles.append({
                    'title':        a.get('title', ''),
                    'body':         a.get('description', ''),
                    'url':          a.get('url', ''),
                    'source':       a.get('source', {}).get('name', ''),
                    'published':    a.get('publishedAt', ''),
                    'material':     material,
                    'manufacturer': manufacturer,
                    'domain_hint':  'economic',
                    'is_trusted':   any(
                        t in a.get('url', '').lower()
                        for t in TRUSTED_SOURCES
                    ),
                })

    except Exception as e:
        print(f"[news_fetcher] NewsAPI error for '{material}': {e}")

    return articles


def fetch_news_for_material(material: str, manufacturer: str) -> list:
    """Fetches news from all sources for a single material."""
    articles = []
    articles.extend(fetch_serpapi_material(material, manufacturer))
    articles.extend(fetch_newsapi_material(material, manufacturer))

    # Remove duplicates by URL
    seen = set()
    unique = []
    for a in articles:
        if a['url'] not in seen and a['url']:
            seen.add(a['url'])
            unique.append(a)

    print(f"[news_fetcher] {material}: {len(unique)} articles fetched")
    return unique


def fetch_all_materials(materials: list, manufacturer: str) -> list:
    """
    Fetches news for ALL materials in parallel.
    Returns one combined list with material tag on each article.
    """
    all_articles = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_news_for_material, m, manufacturer): m
            for m in materials
        }
        for future in futures:
            try:
                all_articles.extend(future.result())
            except Exception as e:
                print(f"[news_fetcher] Failed for material: {e}")

    print(f"[news_fetcher] Total articles fetched: {len(all_articles)}")
    return all_articles