import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


TIMEOUT = 10
BASE_URL = "https://quotes.toscrape.com/"
SLEEP = 6


def fetch_page(url: str) -> str | None:
    """Fetch the HTML content of a URL.

    Returns the response text on HTTP 200, or None if the request times out,
    raises a network error, or returns a non-200 status code.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        print(f"timed out: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"request failed: {e}")
        return None

    if response.status_code != 200:
        print(f"got {response.status_code} for {url}")
        return None

    return response.text


def parse_page(html: str) -> tuple[str, list[str]]:
    """Parse an HTML page and extract visible text and hyperlinks.

    Strips <script> and <style> tags before extracting text so that JavaScript
    and CSS don't pollute the index.

    Returns:
        A (text, links) tuple where text is the visible page content and links
        is a list of raw href values found in <a> tags.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    links = [a["href"] for a in soup.find_all("a", href=True)]

    return text, links


def crawl() -> list[dict]:
    """Crawl the target site starting from BASE_URL using breadth-first search.

    Respects a SLEEP-second politeness window between requests and never
    revisits the same URL twice.

    Returns:
        A list of {"url": str, "text": str} dicts, one per successfully
        fetched page.
    """
    visited: set[str] = set()
    queue: list[str] = [BASE_URL]
    results: list[dict] = []

    while queue:
        url = queue.pop(0)

        if url in visited:
            continue

        print(f"crawling: {url}")
        html = fetch_page(url)
        visited.add(url)

        if html is None:
            continue

        text, links = parse_page(html)
        results.append({"url": url, "text": text})

        for link in links:
            absolute = urljoin(BASE_URL, link)
            if absolute.startswith(BASE_URL) and absolute not in visited:
                queue.append(absolute)

        time.sleep(SLEEP)

    return results