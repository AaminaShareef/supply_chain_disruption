from config.settings import settings

def main():
    print("=== Supply Chain Disruption Prediction System ===")
    print(f"  Model         : {settings.DISTILBERT_MODEL}")
    print(f"  Poll interval : {settings.DEFAULT_POLL_INTERVAL_SECONDS}s")
    print(f"  Similarity    : {settings.SIMILARITY_THRESHOLD}")

    missing = settings.validate()
    if missing:
        print(f"\n[WARNING] Missing API keys: {', '.join(missing)}")
    else:
        print("\n[OK] All API keys present. System ready.")

if __name__ == "__main__":
    main()