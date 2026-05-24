# modelling/domain_classifier.py
# Uses sentence-transformers (DistilBERT) to classify each article
# into one or more supply chain disruption domains.
#
# How it works:
#   1. Converts article text into a vector embedding
#   2. Compares it against domain description embeddings
#   3. Returns domains where similarity exceeds the threshold

from sentence_transformers import SentenceTransformer, util
from config.settings import settings

# --- Domain descriptions — written as natural sentences so the
#     model understands what each domain means semantically ---
DOMAIN_DESCRIPTIONS = {
    'pandemic': (
        'Disease outbreak, virus, epidemic, health emergency, WHO alert, '
        'infection spreading, quarantine, public health crisis, Ebola, COVID'
    ),
    'conflict': (
        'War, military conflict, geopolitical tension, sanctions, trade restrictions, '
        'border dispute, armed forces, missile attack, invasion, troops'
    ),
    'weather': (
        'Natural disaster, flood, typhoon, cyclone, hurricane, earthquake, '
        'wildfire, drought, extreme weather, storm damage, tsunami'
    ),
    'labour': (
        'Workers strike, industrial action, protest, walkout, union dispute, '
        'labour shortage, port workers, dock workers, factory shutdown'
    ),
    'political': (
        'Trade policy, tariff, import duty, government regulation, export ban, '
        'trade war, political instability, election, coup, embargo'
    ),
    'economic': (
        'Commodity price, inflation, currency exchange rate, recession, '
        'oil price, fuel cost, freight rate, shipping cost, market crash'
    ),
}

# Load model once at module level — avoids reloading on every call
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"[domain_classifier] Loading model: {settings.DISTILBERT_MODEL}")
        _model = SentenceTransformer(settings.DISTILBERT_MODEL)
        print(f"[domain_classifier] Model loaded successfully")
    return _model


def classify_article(article: dict) -> dict:
    """
    Classifies a single article into one or more disruption domains.
    Adds 'domains' and 'domain_scores' fields to the article dict.
    """
    model = get_model()

    # Combine title and body for richer context
    text = (article.get('title_clean') or article.get('title', '')) + ' ' + \
           (article.get('body_clean')  or article.get('body',  ''))
    text = text.strip()

    if not text:
        article['domains']       = []
        article['domain_scores'] = {}
        return article

    # Encode article text and all domain descriptions
    article_embedding = model.encode(text,                              convert_to_tensor=True)
    domain_scores     = {}

    for domain, description in DOMAIN_DESCRIPTIONS.items():
        domain_embedding  = model.encode(description, convert_to_tensor=True)
        similarity        = util.cos_sim(article_embedding, domain_embedding).item()
        domain_scores[domain] = round(similarity, 4)

    # Keep domains above the confidence threshold
    threshold      = settings.DOMAIN_CONFIDENCE_THRESHOLD
    matched_domains = [
        d for d, score in domain_scores.items()
        if score >= threshold
    ]

    # Sort matched domains by score descending
    matched_domains.sort(key=lambda d: domain_scores[d], reverse=True)

    # Limit to max domains per article
    matched_domains = matched_domains[:settings.MAX_DOMAINS_PER_ARTICLE]

    article['domains']       = matched_domains
    article['domain_scores'] = domain_scores

    return article