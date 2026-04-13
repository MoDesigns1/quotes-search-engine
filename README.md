# Quotes Search Engine

A simple search engine that crawls quotes.toscrape.com, builds an inverted index,
and lets you search for quotes by keyword. Uses TF-IDF scoring to rank results.

## Install

```
pip install -r requirements.txt
```

## Run

```
python src/main.py
```

This drops you into a prompt where you type commands.

## Commands

**build** - crawl the site and build the index from scratch. Takes a while because
it sleeps between requests to be polite.

```
> build
Starting crawler...
crawling: https://quotes.toscrape.com/
...
Done. Index saved to data/index.json.
```

**load** - load a previously built index from disk. Do this instead of build if
you already have data/index.json.

```
> load
Index loaded successfully. 547 unique words.
```

**find \<query\>** - search for pages containing all the query words, ranked by
TF-IDF score.

```
> find life
Found 3 page(s) containing all of: life:
  https://quotes.toscrape.com/page/2/  (score: 0.0312)
  https://quotes.toscrape.com/  (score: 0.0187)
  https://quotes.toscrape.com/page/3/  (score: 0.0143)

> find love hate
Found 1 page(s) containing all of: love, hate:
  https://quotes.toscrape.com/page/4/  (score: 0.0201)
```

**print \<word\>** - show raw index data for a word: which pages it appears on,
how many times, and at which positions.

```
> print truth
'truth':
  https://quotes.toscrape.com/page/2/
    freq: 3
    positions: [142, 289, 301]
```

**exit** - quit.

## Tests

```
pytest
```

Or to see each test name:

```
pytest -v
```

Tests cover the crawler helpers, indexer (tokenizing, building, save/load), and
search logic (AND queries, ranking, edge cases).
