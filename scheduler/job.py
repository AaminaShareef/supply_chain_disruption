# scheduler/job.py
# Defines the main pipeline job that runs on a schedule.
# This is the function that gets called every 30 minutes.

from ingestion  import fetch_all
from processing import run_pipeline
from modelling  import run_modelling
from storage    import save_articles, get_stats
from datetime   import datetime, timezone


def run_pipeline_job():
    """
    Full pipeline job:
      1. Fetch articles from all sources
      2. Clean and deduplicate
      3. Classify and score
      4. Save to database
    """
    start_time = datetime.now(timezone.utc)
    print(f"\n{'=' * 60}")
    print(f"[job] Pipeline started at {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'=' * 60}")

    try:
        # Phase 2 — Fetch
        articles = fetch_all()
        if not articles:
            print("[job] No articles fetched — skipping this run.")
            return

        # Phase 3 — Clean
        cleaned  = run_pipeline(articles)
        if not cleaned:
            print("[job] No clean articles — skipping this run.")
            return

        # Phase 4 — Classify
        results  = run_modelling(cleaned)
        if not results:
            print("[job] No classified articles — skipping this run.")
            return

        # Phase 5 — Store
        summary  = save_articles(results)

        # Stats
        stats    = get_stats()
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).seconds

        print(f"\n[job] ✅ Pipeline completed in {duration}s")
        print(f"[job] Saved {summary['saved']} new articles")
        print(f"[job] Database totals — "
              f"Critical: {stats['critical']} | "
              f"High: {stats['high']} | "
              f"Medium: {stats['medium']} | "
              f"Low: {stats['low']}")

    except Exception as e:
        print(f"[job] ❌ Pipeline failed: {e}")
        raise