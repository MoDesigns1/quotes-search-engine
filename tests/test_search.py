from src.search import find

INDEX = {
    "hello": {
        "http://a.com": {"freq": 2, "positions": [0, 3]},
        "http://b.com": {"freq": 1, "positions": [0]},
    },
    "world": {
        "http://a.com": {"freq": 1, "positions": [1]},
        "http://c.com": {"freq": 1, "positions": [0]},
    },
    "python": {
        "http://a.com": {"freq": 1, "positions": [2]},
    },
    "_page_lengths": {
        "http://a.com": 4,
        "http://b.com": 3,
        "http://c.com": 2,
    },
}


# single word


def test_single_word_returns_matching_urls():
    urls = [url for url, _ in find(INDEX, "hello")]
    assert "http://a.com" in urls
    assert "http://b.com" in urls


def test_single_word_excludes_non_matching_urls():
    urls = [url for url, _ in find(INDEX, "python")]
    assert urls == ["http://a.com"]


def test_single_word_scores_are_floats():
    results = find(INDEX, "hello")
    for url, score in results:
        assert isinstance(url, str)
        assert isinstance(score, float)


def test_higher_frequency_ranks_first():
    # a.com has freq=2, b.com has freq=1, so a.com should score higher
    results = find(INDEX, "hello")
    assert results[0][0] == "http://a.com"


# multi-word AND logic


def test_multi_word_returns_intersection_only():
    # "hello" is in a.com + b.com; "world" is in a.com + c.com -> only a.com has both
    urls = [url for url, _ in find(INDEX, "hello world")]
    assert urls == ["http://a.com"]


def test_multi_word_excludes_partial_matches():
    results = find(INDEX, "hello world")
    urls = [url for url, _ in results]
    assert "http://b.com" not in urls
    assert "http://c.com" not in urls


def test_word_order_doesnt_matter():
    assert find(INDEX, "hello world") == find(INDEX, "world hello")


# word not in index


def test_unknown_word_returns_empty():
    assert find(INDEX, "javascript") == []


def test_one_unknown_word_in_multi_word_query_returns_empty():
    assert find(INDEX, "hello javascript") == []


# empty query


def test_empty_string_returns_empty():
    assert find(INDEX, "") == []


def test_whitespace_only_returns_empty():
    assert find(INDEX, "   ") == []
