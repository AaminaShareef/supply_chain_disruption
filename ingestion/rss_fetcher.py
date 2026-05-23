# ingestion/rss_fetcher.py
# Reads from WHO, FEMA and Reuters RSS feeds.
# Completely free — no API key needed.

import feedparser

RSS_FEEDS = {
    'pandemic': ['https://www.who.int/rss-feeds/news-english.xml'],
    'weather':  ['https://www.fema.gov/api/open/v1/disasterDeclarations.rss'],
    'conflict': ['http://feeds.reuters.com/Reuters/worldNews'],
}

def fetch_rss(domain: str) -> list:
    articles = []

    for feed_url in RSS_FEEDS.get(domain, []):
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            articles.append({
                'title':       entry.get('title', ''),
                'body':        entry.get('summary', ''),
                'url':         entry.get('link', ''),
                'source':      feed.feed.get('title', 'RSS'),
                'published':   entry.get('published', ''),
                'domain_hint': domain,
            })

    return articles