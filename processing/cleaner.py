# processing/cleaner.py
# Cleans raw article text — removes HTML, fixes broken characters,
# strips extra whitespace and normalises unicode.

import re
import ftfy
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """
    Full cleaning pipeline for a single piece of text.
    Steps:
      1. Fix broken unicode characters (ftfy)
      2. Strip HTML tags
      3. Remove URLs
      4. Remove special characters and symbols
      5. Collapse extra whitespace
    """
    if not text:
        return ''

    # 1. Fix broken unicode (e.g. â€™ → ')
    text = ftfy.fix_text(text)

    # 2. Strip HTML tags
    text = BeautifulSoup(text, 'html.parser').get_text()

    # 3. Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # 4. Remove special characters — keep letters, numbers, punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', ' ', text)

    # 5. Collapse extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def clean_article(article: dict) -> dict:
    """
    Cleans the title and body of a single article dict.
    Returns the same dict with cleaned fields added.
    """
    article['title_clean'] = clean_text(article.get('title', ''))
    article['body_clean']  = clean_text(article.get('body',  ''))
    return article