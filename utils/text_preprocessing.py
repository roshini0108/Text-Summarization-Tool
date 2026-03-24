"""
Utility helpers for text cleaning and tokenization.
"""

import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def ensure_nltk_resources():
    """
    Download required NLTK resources if they are not already available.
    """
    resources = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt_tab": "punkt_tab",
        "corpora/stopwords": "stopwords",
    }

    for resource_path, resource_name in resources.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(resource_name, quiet=True)


import re

def clean_text(text):
    if not text:
        return ""

    # Add space after punctuation (e.g., "word.Sentence")
    text = re.sub(r'([.?!])([A-Z])', r'\1 \2', text)

    # Fix merged words like "helpstudents", "ofdata"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Normalize whitespace
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_word_tokens(text):
    """
    Convert text into lowercase word tokens.
    """
    ensure_nltk_resources()
    return [token.lower() for token in word_tokenize(text)]


def remove_stopwords_and_punctuation(tokens):
    """
    Remove stopwords and punctuation from a list of tokens.
    """
    ensure_nltk_resources()
    stop_words = set(stopwords.words("english"))

    filtered_tokens = []
    for token in tokens:
        if token not in stop_words and token not in string.punctuation and token.isalnum():
            filtered_tokens.append(token)

    return filtered_tokens
