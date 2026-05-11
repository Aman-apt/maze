# I will implement this in future .
from utils import normalize_url
from crawler import BFSCrawler, CrawlerConfig
from crawler_1 import fetch_pages
import aiohttp
import asyncio


def _normalize_outgoing_links(links: set[str], base_url: str = None) -> str:
    for link in links:
        normalized = normalize_url(link, base=base_url)
        if not normalized:
            continue
        if (
            normalized.startswith('mailto:')
            or normalized.startswith('javascript:')
            or normalized.startswith('tel:')
        ):
            continue
    return normalized  

async def main():
    url = 'https://techcrunch.com'
    headers = {
    'User-Agent': (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        )
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        sem = asyncio.Semaphore(20)
        result = await(fetch_pages(session, url, sem))
        for links in result:
            noramal = _normalize_outgoing_links(link)
        print(noramal)
        

asyncio.run(main())