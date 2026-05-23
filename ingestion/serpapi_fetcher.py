# ingestion/serpapi_fetcher.py
# Fetches news from Google News via SerpAPI.

import requests
import os

# --- Trusted news sources ---
TRUSTED_SOURCES = [
    'reuters.com', 'apnews.com', 'bbc.com', 'bloomberg.com',
    'ft.com', 'wsj.com', 'cnbc.com', 'theguardian.com',
    'aljazeera.com', 'forbes.com', 'supplychaindive.com',
    'supplychainbrain.com', 'logisticsmgmt.com'
]

# --- Words that signal low quality articles ---
SPAM_KEYWORDS = [
    'giveaway', 'click here', 'win free', 'make money',
    'crypto', 'nft', 'discount', 'promo', 'buy now',
    'limited offer', 'sponsored', 'advertisement'
]

MIN_TITLE_LENGTH = 20


def get_source_name(source) -> str:
    """Safely extract source name whether it's a string or dict."""
    if isinstance(source, dict):
        return source.get('name', '')
    if isinstance(source, str):
        return source
    return ''


def is_quality_article(article: dict) -> bool:
    title  = (article.get('title')              or '').lower()
    source = get_source_name(article.get('source', '')).lower()
    text   = title + ' ' + source

    # 1. Must have a meaningful title
    if len(title) < MIN_TITLE_LENGTH:
        return False

    # 2. Must not contain spam keywords
    if any(spam in text for spam in SPAM_KEYWORDS):
        return False

    return True


def fetch_serpapi(domain: str, queries: list) -> list:
    articles = []
    api_key  = os.getenv('SERPAPI_KEY')

    if not api_key:
        print("[serpapi_fetcher] No API key found — skipping.")
        return []

    for query in queries:
        url    = 'https://serpapi.com/search'
        params = {
            'engine':  'google_news',
            'q':       query,
            'api_key': api_key,
            'hl':      'en',
            'gl':      'us',
        }

        try:
            resp = requests.get(url, params=params, timeout=15)

            if resp.status_code == 429:
                print(f"[serpapi_fetcher] Rate limit hit for query: {query}")
                continue

            if resp.status_code != 200:
                print(f"[serpapi_fetcher] Error {resp.status_code} for query: {query}")
                continue

            news_results = resp.json().get('news_results', [])

            for a in news_results:
                if not is_quality_article(a):
                    continue

                source_name = get_source_name(a.get('source', ''))
                link        = (a.get('link') or '')
                is_trusted  = any(t in link.lower() for t in TRUSTED_SOURCES)

                articles.append({
                    'title':       a.get('title', ''),
                    'body':        a.get('snippet', ''),
                    'url':         link,
                    'source':      source_name,
                    'published':   a.get('date', ''),
                    'domain_hint': domain,
                    'is_trusted':  is_trusted,
                })

        except Exception as e:
            print(f"[serpapi_fetcher] Exception for query '{query}': {e}")
            continue

    print(f"[serpapi_fetcher] {domain}: {len(articles)} articles fetched")
    return articles