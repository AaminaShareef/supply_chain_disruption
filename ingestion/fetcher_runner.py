# ingestion/fetcher_runner.py
# Runs ALL fetchers in parallel and returns one combined list of articles.
# Sources: NewsAPI, RSS Feeds, SerpAPI (Google News)

from dotenv import load_dotenv
load_dotenv()   # must be called before any os.getenv() in fetchers

from concurrent.futures import ThreadPoolExecutor
from .base_queries import BROAD_QUERIES
from .newsapi_fetcher import fetch_newsapi
from .rss_fetcher import fetch_rss
from .serpapi_fetcher import fetch_serpapi


def fetch_all() -> list:
    all_articles = []
    domains      = list(BROAD_QUERIES.keys())

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = []

        for domain in domains:
            queries = BROAD_QUERIES[domain]

            # Submit all 3 fetchers for each domain in parallel
            futures.append(executor.submit(fetch_newsapi, domain, queries))
            futures.append(executor.submit(fetch_rss,     domain))
            futures.append(executor.submit(fetch_serpapi, domain, queries))

        for f in futures:
            try:
                all_articles.extend(f.result())
            except Exception as e:
                print(f"[fetcher_runner] A fetcher failed: {e}")

    # Remove articles with no title or no url
    all_articles = [
        a for a in all_articles
        if a.get('title') and a.get('url')
    ]

    print(f"[fetcher_runner] Total articles fetched: {len(all_articles)}")
    return all_articles