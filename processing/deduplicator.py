# processing/deduplicator.py
# Removes duplicate articles based on URL and title similarity.
# Must be run AFTER weighted_merge so we always keep the highest
# quality version of each story.

from difflib import SequenceMatcher


def is_similar(title1: str, title2: str, threshold: float = 0.85) -> bool:
    """
    Returns True if two titles are more than threshold% similar.
    Catches articles that are the same story from different sources.
    """
    ratio = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    return ratio >= threshold


def deduplicate(articles: list) -> list:
    """
    Removes duplicates in two passes.
    Since articles are already sorted by quality score (highest first),
    the first occurrence of each story is always the best one.

    Pass 1 — exact URL match
    Pass 2 — similar title match (85% similarity threshold)
    """
    seen_urls   = set()
    seen_titles = []
    unique      = []
    duplicates  = 0

    for article in articles:
        url   = article.get('url',   '').strip()
        title = (article.get('title_clean') or article.get('title', '')).strip()

        # Pass 1 — skip exact duplicate URLs
        if url and url in seen_urls:
            duplicates += 1
            continue

        # Pass 2 — skip articles with very similar titles
        too_similar = any(is_similar(title, seen) for seen in seen_titles)
        if too_similar:
            duplicates += 1
            continue

        # Article is unique — keep it
        seen_urls.add(url)
        seen_titles.append(title)
        unique.append(article)

    print(f"[deduplicator] Kept {len(unique)} unique articles, removed {duplicates} duplicates")
    return unique