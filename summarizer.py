"""
Summarization logic for transformer-based and NLTK-based summaries.
"""

from collections import Counter
import time

try:
    from transformers import pipeline
    _TRANSFORMERS_IMPORT_ERROR = None
except ImportError as error:
    pipeline = None
    _TRANSFORMERS_IMPORT_ERROR = error

from utils.text_preprocessing import (
    clean_text,
    DEPENDENCY_ERROR_MESSAGE,
    ensure_dependencies,
    ensure_nltk_resources,
    get_sentence_tokens,
    get_word_tokens,
    remove_stopwords_and_punctuation,
)


_TRANSFORMER_PIPELINE = None


def get_length_config(summary_length):
    """
    Return summary size settings for each supported method.
    """
    configs = {
        "short": {
            "transformer": {"max_length": 60, "min_length": 20},
            "extractive_sentences": 2,
        },
        "medium": {
            "transformer": {"max_length": 110, "min_length": 40},
            "extractive_sentences": 4,
        },
        "long": {
            "transformer": {"max_length": 160, "min_length": 60},
            "extractive_sentences": 6,
        },
    }
    return configs.get(summary_length, configs["medium"])


def get_transformer_pipeline():
    """
    Load and return the Hugging Face summarization pipeline.
    """
    global _TRANSFORMER_PIPELINE

    if _TRANSFORMERS_IMPORT_ERROR is not None or pipeline is None:
        raise ImportError(DEPENDENCY_ERROR_MESSAGE) from _TRANSFORMERS_IMPORT_ERROR

    if _TRANSFORMER_PIPELINE is None:
        _TRANSFORMER_PIPELINE = pipeline(
            "summarization",
            model="t5-small"
        )

    return _TRANSFORMER_PIPELINE


def summarize_with_transformer(text, summary_length):
    """
    Generate an abstractive summary using a transformer model.
    """
    config = get_length_config(summary_length)["transformer"]
    summarization_pipeline = get_transformer_pipeline()

    result = summarization_pipeline(
        text,
        max_length=config["max_length"],
        min_length=config["min_length"],
        do_sample=False,
        truncation=True,
    )

    return result[0]["summary_text"].strip()


def summarize_with_nltk(text, summary_length):
    """
    Generate an extractive summary using word-frequency scoring.
    """
    ensure_dependencies()
    ensure_nltk_resources()

    cleaned_text = clean_text(text)
    sentences = get_sentence_tokens(cleaned_text)

    if not sentences:
        return "No summary could be generated from the provided text."

    if len(sentences) <= 2:
        return " ".join(sentences)

    word_tokens = get_word_tokens(cleaned_text)
    filtered_words = remove_stopwords_and_punctuation(word_tokens)

    if not filtered_words:
        return "No meaningful words were found to build a summary."

    word_frequencies = Counter(filtered_words)
    max_frequency = max(word_frequencies.values())

    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_scores = {}

    for sentence in sentences:
        sentence_words = remove_stopwords_and_punctuation(get_word_tokens(sentence))
        if not sentence_words:
            continue

        sentence_scores[sentence] = sum(
            word_frequencies.get(word, 0) for word in sentence_words
        )

    if not sentence_scores:
        return "No summary could be generated from the provided text."

    sentence_count = min(
        get_length_config(summary_length)["extractive_sentences"],
        len(sentences),
    )

    ranked_sentences = sorted(
        sentence_scores,
        key=sentence_scores.get,
        reverse=True,
    )[:sentence_count]

    summary_sentences = [sentence for sentence in sentences if sentence in ranked_sentences]

    return " ".join(summary_sentences).strip()


def summarize_text(text, method, summary_length):
    """
    Route the request to the selected summarization method.
    """
    if not text or not text.strip():
        return "No input text provided."

    cleaned_text = clean_text(text)

    if not cleaned_text:
        return "No input text provided."

    try:
        if method == "1":
            try:
                return summarize_with_transformer(cleaned_text, summary_length)
            except Exception:
                return "⚠️ Transformer failed. Using NLTK instead.\n" + summarize_with_nltk(cleaned_text, summary_length)

        if method == "2":
            return summarize_with_nltk(cleaned_text, summary_length)

        return "Invalid summarization method selected."

    except Exception as error:
        return f"Unable to generate summary: {error}"


def compare_summaries(text, summary_length):
    """
    Return summaries from both models.
    """
    transformer_summary = summarize_with_transformer(text, summary_length)
    nltk_summary = summarize_with_nltk(text, summary_length)

    return {
        "transformer": transformer_summary,
        "nltk": nltk_summary
    }


def compare_summaries_with_timing(text, summary_length):
    """
    Return both summaries along with their execution times.
    """
    try:
        transformer_start = time.perf_counter()
        transformer_summary = summarize_with_transformer(text, summary_length)
        transformer_time = time.perf_counter() - transformer_start
    except Exception:
        transformer_start = time.perf_counter()
        transformer_summary = "⚠️ Transformer failed. Using NLTK instead.\n" + summarize_with_nltk(text, summary_length)
        transformer_time = time.perf_counter() - transformer_start

    nltk_start = time.perf_counter()
    nltk_summary = summarize_with_nltk(text, summary_length)
    nltk_time = time.perf_counter() - nltk_start

    return {
        "transformer": transformer_summary,
        "nltk": nltk_summary,
        "transformer_time": transformer_time,
        "nltk_time": nltk_time,
    }
