import math


def find(index: dict, query: str) -> list[tuple[str, float]]:
    """Search the index for pages containing all query words.

    Args:
        index: Inverted index produced by :func:`indexer.build_index`.
        query: Space-separated search terms (case-insensitive assumed by caller).

    Returns:
        List of ``(url, score)`` tuples sorted by TF-IDF score descending.
        Returns ``[]`` for an empty query, an unknown word, or no matching pages.
    """
    words = query.strip().lower().split()
    if not words:
        return []

    page_lengths: dict[str, int] = index.get("_page_lengths", {})
    total_pages = len(page_lengths)

    # guard against searching for the internal metadata key
    for word in words:
        if word not in index or word == "_page_lengths":
            return []

    # AND semantics: only pages that contain every query word
    url_sets = [set(index[w].keys()) for w in words]
    urls = url_sets[0].intersection(*url_sets[1:])
    if not urls:
        return []

    scored: list[tuple[str, float]] = []
    for url in urls:
        score = 0.0
        for word in words:
            tf = index[word][url]["freq"] / page_lengths[url]
            idf = math.log(total_pages / len(index[word]))
            score += tf * idf
        scored.append((url, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored