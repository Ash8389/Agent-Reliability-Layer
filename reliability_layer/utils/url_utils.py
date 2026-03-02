"""
URL utilities.
"""

import re
from typing import List


def normalize_url(url: str) -> str:
    """Strips https://, http://, www., trailing slashes, and lowercases the URL."""
    url = url.lower().strip()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    url = url.rstrip('/')
    return url


def deduplicate_urls(urls: List[str]) -> List[str]:
    """Deduplicates a list of URLs."""
    seen = set()
    result = []
    for url in urls:
        normalized = normalize_url(url)
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)
    return result
