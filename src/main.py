from crawler import crawl
from indexer import build_index, save_index


def handle_build():
    print("Starting crawler...")
    results = crawl()
    print(f"Crawled {len(results)} pages.")

    print("Building index...")
    index = build_index(results)
    print(f"Indexed {len(index)} unique words.")

    print("Saving index...")
    save_index(index)
    print("Done. Index saved to data/index.json.")


while True:
    command = input("\n> ").strip().lower()

    if command == "build":
        handle_build()
    elif command in ("exit", "quit"):
        break
    elif command == "":
        continue
    else:
        print(f"Unknown command: '{command}'. Available commands: build, exit")
