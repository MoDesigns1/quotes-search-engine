"""Command-line shell for the quotes search engine.

Supported commands:
    build           Crawl the site, build the index, and save it to disk.
    load            Load a previously saved index from disk.
    find <query>    Return all pages containing every query word, ranked by TF-IDF.
    print <word>    Show the raw index entry for a word (frequency + positions).
    exit / quit     Leave the shell.
"""

import math
from crawler import crawl
from indexer import build_index, save_index, load_index


index: dict | None = None


def handle_build() -> None:
    """Crawl the site, build the inverted index, and write it to data/index.json."""
    global index
    print("Starting crawler...")
    results = crawl()
    print(f"Crawled {len(results)} pages.")

    print("Building index...")
    index = build_index(results)
    print(f"Indexed {len(index)} unique words.")

    print("Saving index...")
    save_index(index)
    print("Done. Index saved to data/index.json.")


def handle_load() -> None:
    """Load a previously built index from data/index.json."""
    global index
    index = load_index()
    if index:
        print(f"Index loaded successfully. {len(index)} unique words.")


def handle_find(query: str) -> None:
    """Search for pages containing all words in *query* and rank by TF-IDF.

    Args:
        query: Raw query string from the user (may be empty).
    """
    if index is None:
        print("Index not loaded. Run 'load' or 'build' first.")
        return

    if not query.strip():
        print("Usage: find <word> [word ...]")
        return

    page_lengths = index.get("_page_lengths", {})
    if not page_lengths:
        print("Rebuild the index to enable TF-IDF ranking.")
        return

    words = query.strip().lower().split()
    for word in words:
        if word not in index or word == "_page_lengths":
            print(f"'{word}' not found in index.")
            return

    url_sets = [set(index[w].keys()) for w in words]
    urls = url_sets[0].intersection(*url_sets[1:])
    if not urls:
        print(f"No pages contain all of: {', '.join(words)}")
        return

    total_pages = len(page_lengths)
    scored: list[tuple[str, float]] = []
    for url in urls:
        score = 0.0
        for word in words:
            tf = index[word][url]["freq"] / page_lengths[url]
            idf = math.log(total_pages / len(index[word]))
            score += tf * idf
        scored.append((url, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    print(f"Found {len(scored)} page(s) containing all of: {', '.join(words)}:")
    for url, score in scored:
        print(f"  {url}  (score: {score:.4f})")


def handle_print(word: str) -> None:
    """Print the raw inverted index entry for *word*.

    Args:
        word: The word to look up (may be empty).
    """
    if index is None:
        print("Index not loaded. Run 'load' or 'build' first.")
        return

    word = word.strip().lower()
    if not word:
        print("Usage: print <word>")
        return

    if word == "_page_lengths":
        print("'_page_lengths' is an internal key, not a searchable word.")
        return

    if word not in index:
        print(f"'{word}' not found in index.")
        return

    print(f"'{word}':")
    for url, data in index[word].items():
        print(f"  {url}")
        print(f"    freq: {data['freq']}")
        print(f"    positions: {data['positions']}")


if __name__ == "__main__":
    while True:
        command = input("\n> ").strip()
        lower = command.lower()

        if lower == "build":
            handle_build()
        elif lower == "load":
            handle_load()
        elif lower.startswith("find "):
            handle_find(command[5:])
        elif lower == "find":
            print("Usage: find <word> [word ...]")
        elif lower.startswith("print "):
            handle_print(command[6:])
        elif lower == "print":
            print("Usage: print <word>")
        elif lower in ("exit", "quit"):
            break
        elif lower == "":
            continue
        else:
            print(f"Unknown command: '{command}'. Available commands: build, load, find <word>, print <word>, exit")