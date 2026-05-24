from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    NEWSAPI_KEY                   = os.getenv("NEWSAPI_KEY", "")
    TWITTER_BEARER_TOKEN          = os.getenv("TWITTER_BEARER_TOKEN", "")
    SERPAPI_KEY                   = os.getenv("SERPAPI_KEY", "")
    MEDIASTACK_KEY                = os.getenv("MEDIASTACK_KEY", "")
    OPENROUTER_API_KEY            = os.getenv("OPENROUTER_API_KEY", "")
    DISTILBERT_MODEL              = os.getenv("DISTILBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    SIMILARITY_THRESHOLD          = float(os.getenv("SIMILARITY_THRESHOLD", "0.82"))
    DOMAIN_CONFIDENCE_THRESHOLD   = float(os.getenv("DOMAIN_CONFIDENCE_THRESHOLD", "0.40"))
    MAX_DOMAINS_PER_ARTICLE       = int(os.getenv("MAX_DOMAINS_PER_ARTICLE", "3"))
    POSTGRES_URL                  = os.getenv("POSTGRES_URL", "postgresql://user:pass@localhost:5432/supply_chain")
    REDIS_URL                     = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEFAULT_POLL_INTERVAL_SECONDS = int(os.getenv("DEFAULT_POLL_INTERVAL_SECONDS", "1800"))
    ALERT_POLL_INTERVAL_SECONDS   = int(os.getenv("ALERT_POLL_INTERVAL_SECONDS", "300"))
    ALERT_DURATION_HOURS          = int(os.getenv("ALERT_DURATION_HOURS", "6"))

    def validate(self):
        mandatory = ["NEWSAPI_KEY", "TWITTER_BEARER_TOKEN", "SERPAPI_KEY", "MEDIASTACK_KEY"]
        return [k for k in mandatory if not getattr(self, k)]

settings = Settings()