from ingestion  import fetch_all
from processing import run_pipeline
from modelling  import run_modelling
from storage    import init_db, save_articles, get_alerts, get_stats

# Phase 2 — Fetch
articles = fetch_all()

# Phase 3 — Clean
cleaned  = run_pipeline(articles)

# Phase 4 — Classify and score
results  = run_modelling(cleaned)

# Phase 5 — Store
init_db()
save_articles(results)

# Print stats
stats = get_stats()
print(f"\nDatabase Summary:")
print(f"  Total    : {stats['total']}")
print(f"  Critical : {stats['critical']}")
print(f"  High     : {stats['high']}")
print(f"  Medium   : {stats['medium']}")
print(f"  Low      : {stats['low']}")

# Print top 5 alerts
print("\nTop 5 High Risk Alerts:")
print("=" * 60)
alerts = get_alerts(risk_level='high', limit=5)
for a in alerts:
    print(f"Title  : {a['title']}")
    print(f"Source : {a['source']}")
    print(f"Domains: {', '.join(a['domains'])}")
    print(f"Risk   : {a['risk_score']} ({a['risk_level'].upper()})")
    print("-" * 60)