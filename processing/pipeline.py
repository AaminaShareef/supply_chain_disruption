# processing/pipeline.py
# Master pipeline for Phase 3 — connects all processing steps in order.
#
# Order of operations:
#   1. Clean text        (cleaner.py)
#   2. Filter English    (language_filter.py)
#   3. Weighted merge    (merger.py)
#   4. Deduplicate       (deduplicator.py)

from .cleaner         import clean_article
from .language_filter import filter_english
from .merger          import weighted_merge
from .deduplicator    import deduplicate


def run_pipeline(articles: list) -> list:
    """
    Takes raw articles from Phase 2 and returns
    a clean, ranked, deduplicated list ready for AI modelling.
    """
    print(f"\n[pipeline] Starting with {len(articles)} raw articles")
    print("─" * 50)

    # Step 1 — Clean title and body text
    print("[pipeline] Step 1: Cleaning text...")
    articles = [clean_article(a) for a in articles]

    # Step 2 — Keep only English articles
    print("[pipeline] Step 2: Filtering non-English articles...")
    articles = filter_english(articles)

    # Step 3 — Score and rank by quality
    print("[pipeline] Step 3: Scoring and ranking by quality...")
    articles = weighted_merge(articles)

    # Step 4 — Remove duplicates (keeps highest scoring version)
    print("[pipeline] Step 4: Removing duplicates...")
    articles = deduplicate(articles)

    print("─" * 50)
    print(f"[pipeline] Done! {len(articles)} clean articles ready for modelling\n")

    return articles