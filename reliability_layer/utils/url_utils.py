import re

def normalize_url(url: str) -> str:
    """
    Normalize a URL to a consistent comparable string.
    Strips protocol, www prefix, and trailing slashes.
    """
    url = url.strip().lower()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    url = url.rstrip('/')
    return url

def normalize_citation(citation: str) -> str:
    """
    Normalize a plain text citation name.
    e.g. 'World Health Organization (WHO)'
      -> 'world health organization who'
    e.g. 'Reuters News Agency'
      -> 'reuters news agency'
    """
    citation = citation.lower().strip()
    # Remove bracketed content like (WHO)
    citation = re.sub(r'\(.*?\)', '', citation)
    # Remove punctuation
    citation = re.sub(r'[^\w\s]', '', citation)
    # Collapse multiple spaces
    citation = re.sub(r'\s+', ' ', citation).strip()
    return citation

def deduplicate_urls(urls: list[str]) -> list[str]:
    """Remove duplicate URLs after normalization."""
    seen = set()
    result = []
    for url in urls:
        key = normalize_url(url)
        if key not in seen:
            seen.add(key)
            result.append(url)
    return result
