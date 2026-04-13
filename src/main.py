import math
from crawler import crawl
from indexer import build_index, save_index, load_index


index = None


def handle_build():
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


def handle_load():
    global index
    index = load_index()
    if index:
        print(f"Index loaded successfully. {len(index)} unique words.")


def handle_find(query):
    if index is None:
        print("Index not loaded. Run 'load' or 'build' first.")
        return

    page_lengths = index.get("_page_lengths", {})
    if not page_lengths:
        print("Rebuild the index to enable TF-IDF ranking.")
        return

    words = query.split()
    for word in words:
        if word not in index:
            print(f"'{word}' not found in index.")
            return

    # find pages that contain every query word
    url_sets = [set(index[w].keys()) for w in words]
    urls = url_sets[0].intersection(*url_sets[1:])
    if not urls:
        print(f"No pages contain all of: {', '.join(words)}")
        return

    total_pages = len(page_lengths)

    # rank results with TF-IDF
    # tf  = freq on this page / total words on page  (how much this page talks about the word)
    # idf = log(total pages / pages containing word) (rarer words get more weight)
    # score = sum of tf*idf across all query words, higher is better
    scored = []
    for url in urls:
        score = 0
        for word in words:
            tf = index[word][url]["freq"] / page_lengths[url]
            idf = math.log(total_pages / len(index[word]))
            score += tf * idf
        scored.append((url, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    print(f"Found {len(scored)} page(s) containing all of: {', '.join(words)}:")
    for url, score in scored:
        print(f"  {url}  (score: {score:.4f})")


def handle_print(word):
    if index is None:
        print("Index not loaded. Run 'load' or 'build' first.")
        return
    if word not in index:
        print(f"'{word}' not found in index.")
        return
    print(f"'{word}':")
    for url, data in index[word].items():
        print(f"  {url}")
        print(f"    freq: {data['freq']}")
        print(f"    positions: {data['positions']}")


while True:
    command = input("\n> ").strip().lower()

    if command == "build":
        handle_build()
    elif command == "load":
        handle_load()
    elif command.startswith("find "):
        handle_find(command[5:].strip())
    elif command.startswith("print "):
        handle_print(command[6:].strip())
    elif command in ("exit", "quit"):
        break
    elif command == "":
        continue
    else:
        print(f"Unknown command: '{command}'. Available commands: build, load, find <word>, print <word>, exit")
