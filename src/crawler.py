import requests
from bs4 import BeautifulSoup


TIMEOUT = 10


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
