# main.py
# Entry point for the Supply Chain Disruption Prediction System.
# Run: python main.py

from dotenv          import load_dotenv
load_dotenv()

from config.settings import settings
from storage         import init_db
from scheduler       import start_scheduler


def main():
    print("=== Supply Chain Disruption Prediction System ===")
    print(f"  Model         : {settings.DISTILBERT_MODEL}")
    print(f"  Poll interval : {settings.DEFAULT_POLL_INTERVAL_SECONDS // 60} minutes")
    print(f"  Similarity    : {settings.SIMILARITY_THRESHOLD}")

    # Validate API keys
    missing = settings.validate()
    if missing:
        print(f"\n[WARNING] Missing API keys: {', '.join(missing)}")
        print("  Fill in .env before running.\n")
        return

    # Initialise database
    init_db()

    # Start the scheduler — runs forever until Ctrl+C
    start_scheduler()


if __name__ == "__main__":
    main()