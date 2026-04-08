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
    words = query.split()
    for word in words:
        if word not in index:
            print(f"'{word}' not found in index.")
            return
    url_sets = [set(index[w].keys()) for w in words]
    urls = sorted(url_sets[0].intersection(*url_sets[1:]))
    if not urls:
        print(f"No pages contain all of: {', '.join(words)}")
        return
    print(f"Found {len(urls)} page(s) containing all of: {', '.join(words)}:")
    for url in urls:
        print(f"  {url}")


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
