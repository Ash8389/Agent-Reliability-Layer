"""
Text utilities.
"""

import string


def truncate(text: str, max_chars: int = 300) -> str:
    """Truncates text to a maximum number of characters."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def word_overlap_ratio(text_a: str, text_b: str) -> float:
    """Calculates the ratio of overlapping words between two strings."""
    words_a = set(normalize_text(text_a).split())
    words_b = set(normalize_text(text_b).split())
    
    if not words_a and not words_b:
        return 1.0
    if not words_a or not words_b:
        return 0.0
        
    overlap = words_a.intersection(words_b)
    return len(overlap) / max(len(words_a), len(words_b))


def normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase, stripping, and removing punctuation."""
    text = text.lower().strip()
    return text.translate(str.maketrans('', '', string.punctuation))
