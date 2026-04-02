import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


TIMEOUT = 10
BASE_URL = "https://quotes.toscrape.com/"
SLEEP = 6


def fetch_page(url):
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


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    # strip out script/style tags so we don't get js/css in the text
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    links = [a["href"] for a in soup.find_all("a", href=True)]

    return text, links


def crawl():
    visited = set()
    queue = [BASE_URL]
    results = []

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
            if not re.match(r"^/page/\d+/$", link):
                continue

            absolute = urljoin(url, link)

            if absolute not in visited:
                queue.append(absolute)

        time.sleep(SLEEP)

    return results
