import aiohttp
import asyncio
from urllib.parse import urlparse, urljoin, urlunparse
from html.parser import HTMLParser
from typing import Optional

def normalize_url(url: str, base: Optional[str] = None) -> Optional[str]:
    """
    Normalize the URL by removing the fragments(#) because they are used of user interactions purpose.
    """
    try:
        if base:
            url = urljoin(base, url)

        parsed = urlparse(url.strip())

        if parsed.scheme not in {"http", "https"}:
            return None

        # Drop fragment, keep query.
        normalized = parsed._replace(fragment="")
        return urlunparse(normalized)
    except Exception:
        return None

def url_host(url: str) -> str:
    return urlparse(url).netloc.lower()


def safe_filename_from_url(url: str, suffix: str = "") -> str:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
    return f"{h}{suffix}"


def content_type_from_headers(headers: dict[str, str]) -> str:
    ct = headers.get("Content-Type", "")
    return ct.split(";", 1)[0].strip().lower()


def guess_extension(content_type: str) -> str:
    if "text/html" in content_type:
        return ".html"
    if "text/plain" in content_type:
        return ".txt"
    if "application/json" in content_type:
        return ".json"
    return ".bin"

from datetime import datetime, timezone
def utc_now():
    return datetime.now(timezone.utc).isoformat()


# testing the functionalities
if __name__ == "__main__":
    url = 'https://techrunch.com/home/a=12&k=323/#results'
    normalized = normalize_url(url)
    print(normalized)

    # It will return this
    # https://techrunch.com/home/a=12&k=323/ ---> A normalied url without the fragment