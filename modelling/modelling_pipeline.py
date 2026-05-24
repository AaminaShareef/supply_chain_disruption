# modelling/modelling_pipeline.py
# Master pipeline for Phase 4 — connects classification and risk scoring.
#
# Order of operations:
#   1. Classify each article into disruption domains
#   2. Calculate risk score for each article
#   3. Filter out articles with no matched domains
#   4. Sort by risk score descending

from .domain_classifier import classify_article
from .risk_scorer       import calculate_risk_score


def run_modelling(articles: list) -> list:
    """
    Takes clean articles from Phase 3 and returns
    classified, risk-scored articles ready for storage.
    """
    print(f"\n[modelling] Starting with {len(articles)} clean articles")
    print("─" * 50)

    # Step 1 — Classify each article into domains
    print("[modelling] Step 1: Classifying articles into domains...")
    articles = [classify_article(a) for a in articles]

    # Step 2 — Calculate risk score for each article
    print("[modelling] Step 2: Calculating risk scores...")
    articles = [calculate_risk_score(a) for a in articles]

    # Step 3 — Filter out articles with no matched domains
    before   = len(articles)
    articles = [a for a in articles if a.get('domains')]
    filtered = before - len(articles)
    print(f"[modelling] Step 3: Filtered out {filtered} unrelated articles")

    # Step 4 — Sort by risk score descending
    articles.sort(key=lambda a: a['risk_score'], reverse=True)

    # Summary
    critical = [a for a in articles if a.get('risk_level') == 'critical']
    high     = [a for a in articles if a.get('risk_level') == 'high']
    medium   = [a for a in articles if a.get('risk_level') == 'medium']
    low      = [a for a in articles if a.get('risk_level') == 'low']

    print("─" * 50)
    print(f"[modelling] Done! {len(articles)} articles classified")
    print(f"  🔴 Critical : {len(critical)}")
    print(f"  🟠 High     : {len(high)}")
    print(f"  🟡 Medium   : {len(medium)}")
    print(f"  🟢 Low      : {len(low)}\n")

    return articles