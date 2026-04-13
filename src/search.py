import math


def find(index, query):
    # return a list of (url, score) sorted by TF-IDF descending or 
    # [] for an empty query, an unknown word, or no matching pages
    
    words = query.strip().split()
    if not words:
        return []

    page_lengths = index.get("_page_lengths", {})
    total_pages = len(page_lengths)

    for word in words:
        if word not in index:
            return []

    url_sets = [set(index[w].keys()) for w in words]
    urls = url_sets[0].intersection(*url_sets[1:])
    if not urls:
        return []

    scored = []
    for url in urls:
        score = 0
        for word in words:
            tf = index[word][url]["freq"] / page_lengths[url]
            idf = math.log(total_pages / len(index[word]))
            score += tf * idf
        scored.append((url, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
