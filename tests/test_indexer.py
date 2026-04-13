import json
import os
import tempfile
import pytest

from src.indexer import tokenize, build_index, save_index, load_index


# tokenize

def test_tokenize_lowercases():
    assert tokenize("Hello World") == ["hello", "world"]


def test_tokenize_strips_punctuation():
    assert tokenize("it's great! really...") == ["it", "s", "great", "really"]


def test_tokenize_mixed_case_and_punctuation():
    assert tokenize("Don't STOP.") == ["don", "t", "stop"]


def test_tokenize_empty_string():
    assert tokenize("") == []


def test_tokenize_numbers_ignored():
    # digits are not matched by [a-z]+
    assert tokenize("abc 123 def") == ["abc", "def"]


# build_index

DOCS = [
    {"url": "http://a.com", "text": "the cat sat on the mat"},
    {"url": "http://b.com", "text": "the cat in the hat"},
]


def test_frequency_counts():
    index = build_index(DOCS)
    # "the" appears twice in doc a
    assert index["the"]["http://a.com"]["freq"] == 2
    # "the" appears twice in doc b
    assert index["the"]["http://b.com"]["freq"] == 2
    # "cat" appears once in each doc
    assert index["cat"]["http://a.com"]["freq"] == 1
    assert index["cat"]["http://b.com"]["freq"] == 1


def test_position_tracking():
    index = build_index(DOCS)
    # "the cat sat on the mat" -> the=0,4  cat=1  sat=2  on=3  mat=5
    assert index["the"]["http://a.com"]["positions"] == [0, 4]
    assert index["cat"]["http://a.com"]["positions"] == [1]
    assert index["mat"]["http://a.com"]["positions"] == [5]


def test_word_only_in_one_doc():
    index = build_index(DOCS)
    assert "http://b.com" not in index["sat"]
    assert "http://a.com" not in index["hat"]


def test_page_lengths_stored():
    index = build_index(DOCS)
    # "the cat sat on the mat" -> 6 words
    assert index["_page_lengths"]["http://a.com"] == 6
    # "the cat in the hat" -> 5 words
    assert index["_page_lengths"]["http://b.com"] == 5


def test_empty_crawl_results():
    index = build_index([])
    assert index == {"_page_lengths": {}}


# save / load roundtrip

def test_save_load_roundtrip():
    index = build_index(DOCS)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "index.json")
        save_index(index, path)
        loaded = load_index(path)

    assert loaded == index


def test_load_missing_file_returns_empty(capsys):
    result = load_index("/nonexistent/path/index.json")
    assert result == {}


def test_save_creates_missing_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "nested", "dir", "index.json")
        save_index({"hello": {}}, path)
        assert os.path.exists(path)
