import re
import json
import os

DEFAULT_INDEX_PATH = os.path.join(os.path.dirname(__file__), "data", "index.json")

def tokenize(text: str) -> list[str]:
    """Convert raw text into a list of lowercase alphabetic tokens.

    Digits and punctuation are discarded.

    Args:
        text: Raw page text.

    Returns:
        Ordered list of tokens.
    """
    return re.findall(r"[a-z]+", text.lower())


def build_index(crawl_results: list[dict]) -> dict:
    """Build an inverted index from a list of crawled page records.

    Each record must have ``"url"`` and ``"text"`` keys. For every token in a
    page the index stores its frequency and all word positions, enabling
    TF-IDF ranking.

    Time complexity: O(N) where N is the total number of tokens across all pages.

    Args:
        crawl_results: Output of :func:`crawler.crawl`.

    Returns:
        Inverted index dict as described in the module docstring.
    """
    index: dict = {}
    page_lengths: dict[str, int] = {}

    for doc in crawl_results:
        url: str = doc["url"]
        words = tokenize(doc["text"])
        page_lengths[url] = len(words)

        for position, word in enumerate(words):
            if word not in index:
                index[word] = {}
            if url not in index[word]:
                index[word][url] = {"freq": 0, "positions": []}

            index[word][url]["freq"] += 1
            index[word][url]["positions"].append(position)

    index["_page_lengths"] = page_lengths
    return index


def save_index(index: dict, path: str = DEFAULT_INDEX_PATH) -> None:
    """Serialise the index to a JSON file, creating parent directories if needed.

    Args:
        index: Index dict produced by :func:`build_index`.
        path: Destination file path.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(index, f)


def load_index(path: str = DEFAULT_INDEX_PATH) -> dict:
    """Deserialise an index from a JSON file.

    Returns an empty dict and prints an error message if the file does not exist.

    Args:
        path: Path to a previously saved index file.

    Returns:
        Index dict, or ``{}`` if the file is missing.
    """
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run 'build' first.")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)