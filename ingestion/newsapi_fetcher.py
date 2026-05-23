# ingestion/newsapi_fetcher.py
# Fetches news articles from NewsAPI.org, one domain at a time.

import requests
import os

def fetch_newsapi(domain: str, queries: list) -> list:
    articles = []

    for query in queries:
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q':         query,
            'language':  'en',
            'sortBy':    'publishedAt',
            'pageSize':  20,
            'apiKey':    os.getenv('NEWSAPI_KEY')
        }

        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code == 200:
            for a in resp.json().get('articles', []):
                articles.append({
                    'title':       a.get('title', ''),
                    'body':        a.get('description', ''),
                    'url':         a.get('url', ''),
                    'source':      a.get('source', {}).get('name', ''),
                    'published':   a.get('publishedAt', ''),
                    'domain_hint': domain,
                })

    return articles