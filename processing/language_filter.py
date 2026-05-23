# processing/language_filter.py
# Filters out non-English articles using langdetect.
# We only want English articles for the AI model to process.

from langdetect import detect, LangDetectException


def is_english(text: str) -> bool:
    """
    Returns True if the text is detected as English.
    Returns False for non-English or undetectable text.
    """
    if not text or len(text.strip()) < 20:
        return False

    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False


def filter_english(articles: list) -> list:
    """
    Takes a list of articles and returns only English ones.
    Uses the cleaned title + body for detection.
    """
    english  = []
    rejected = 0

    for article in articles:
        # Use cleaned text if available, otherwise raw
        text = article.get('title_clean') or article.get('title', '')
        text += ' ' + (article.get('body_clean') or article.get('body', ''))

        if is_english(text):
            english.append(article)
        else:
            rejected += 1

    print(f"[language_filter] Kept {len(english)} English articles, rejected {rejected}")
    return english