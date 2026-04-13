import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from unittest.mock import patch, MagicMock
from crawler import fetch_page, parse_page, crawl

# fetch_page

def test_fetch_page_returns_html_on_200():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>hello</html>"

    with patch("crawler.requests.get", return_value=mock_response):
        result = fetch_page("https://example.com")

    assert result == "<html>hello</html>"


def test_fetch_page_returns_none_on_404():
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("crawler.requests.get", return_value=mock_response):
        result = fetch_page("https://example.com/missing")

    assert result is None


def test_fetch_page_returns_none_on_timeout():
    import requests as req

    with patch("crawler.requests.get", side_effect=req.exceptions.Timeout):
        result = fetch_page("https://example.com")

    assert result is None


def test_fetch_page_returns_none_on_connection_error():
    import requests as req

    with patch("crawler.requests.get", side_effect=req.exceptions.ConnectionError):
        result = fetch_page("https://example.com")

    assert result is None


# parse_page

def test_parse_page_extracts_text():
    html = "<html><body><p>Hello world</p></body></html>"
    text, _ = parse_page(html)
    assert "Hello" in text
    assert "world" in text


def test_parse_page_strips_script_and_style():
    html = """
    <html><body>
        <script>var x = 1;</script>
        <style>.foo { color: red; }</style>
        <p>Visible text</p>
    </body></html>
    """
    text, _ = parse_page(html)
    assert "var x" not in text
    assert "color: red" not in text
    assert "Visible text" in text


def test_parse_page_extracts_links():
    html = """
    <html><body>
        <a href="/page/2/">next</a>
        <a href="/author/einstein/">Einstein</a>
    </body></html>
    """
    _, links = parse_page(html)
    assert "/page/2/" in links
    assert "/author/einstein/" in links


def test_parse_page_ignores_anchors_without_href():
    html = '<html><body><a name="top">anchor</a><a href="/page/2/">link</a></body></html>'
    _, links = parse_page(html)
    assert links == ["/page/2/"]


# crawl

def test_crawl_visits_linked_pages():
    # page 1 links to page 2, page 2 has no links
    page1 = '<html><body><p>Page one</p><a href="/page/2/">next</a></body></html>'
    page2 = '<html><body><p>Page two</p></body></html>'

    def fake_get(url, **_):
        mock = MagicMock()
        mock.status_code = 200
        mock.text = page2 if "page/2" in url else page1
        return mock

    with patch("crawler.requests.get", side_effect=fake_get), \
         patch("crawler.time.sleep"):  # don't actually sleep in tests
        results = crawl()

    urls_visited = [r["url"] for r in results]
    assert any("page/2" in url for url in urls_visited), "should have followed the link to page 2"


def test_crawl_does_not_visit_same_page_twice():
    # page links back to itself - should only be visited once
    page = '<html><body><a href="/">home</a></body></html>'

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = page

    with patch("crawler.requests.get", return_value=mock_response), \
         patch("crawler.time.sleep"):
        results = crawl()

    # base URL should only appear once in results
    base_hits = [r for r in results if r["url"] == "https://quotes.toscrape.com/"]
    assert len(base_hits) == 1


def test_crawl_skips_failed_pages():
    # first page fetches fine and links to page 2, page 2 returns 500
    page1 = '<html><body><p>ok</p><a href="/page/2/">next</a></body></html>'

    def fake_get(url, **_):
        mock = MagicMock()
        if "page/2" in url:
            mock.status_code = 500
        else:
            mock.status_code = 200
            mock.text = page1
        return mock

    with patch("crawler.requests.get", side_effect=fake_get), \
         patch("crawler.time.sleep"):
        results = crawl()

    # only page 1 should be in results - page 2 failed so nothing was saved for it
    assert len(results) == 1
    assert "page/2" not in results[0]["url"]
