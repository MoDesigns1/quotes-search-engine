import re
import json
import os

DEFAULT_INDEX_PATH = os.path.join(os.path.dirname(__file__), "data", "index.json")


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return words


def build_index(crawl_results: list[dict]) -> dict:
    # crawl_results is a list of {"url": ..., "text": ...} dicts
    index = {}
    page_lengths = {}  # url -> total word count, used for TF-IDF scoring

    for doc in crawl_results:
        url = doc["url"]
        words = tokenize(doc["text"])
        page_lengths[url] = len(words)

        for position, word in enumerate(words):
            if word not in index:
                index[word] = {}

            if url not in index[word]:
                index[word][url] = {"freq": 0, "positions": []}

            index[word][url]["freq"] += 1
            index[word][url]["positions"].append(position)

    # stored under a special key so save/load picks it up automatically
    index["_page_lengths"] = page_lengths
    return index


def save_index(index: dict, path: str = DEFAULT_INDEX_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(index, f)


def load_index(path: str = DEFAULT_INDEX_PATH) -> dict:
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run the crawler and build the index first.")
        return {}
    with open(path, "r") as f:
        return json.load(f)
