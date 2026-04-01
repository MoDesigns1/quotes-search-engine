import re
import json
import os


def tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    return words


def build_index(crawl_results):
    # crawl_results is a list of {"url": ..., "text": ...} dicts
    index = {}

    for doc in crawl_results:
        url = doc["url"]
        words = tokenize(doc["text"])

        for position, word in enumerate(words):
            if word not in index:
                index[word] = {}

            if url not in index[word]:
                index[word][url] = {"freq": 0, "positions": []}

            index[word][url]["freq"] += 1
            index[word][url]["positions"].append(position)

    return index


def save_index(index, path="data/index.json"):
    with open(path, "w") as f:
        json.dump(index, f)


def load_index(path="data/index.json"):
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run the crawler and build the index first.")
        return {}
    with open(path, "r") as f:
        return json.load(f)
