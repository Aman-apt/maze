import aiohttp
import asyncio
import json
from dataclasses import dataclass, field
from utils import (
    normalize_url,
    url_host,
    content_type_from_headers,
    guess_extension,
    safe_filename_from_url,
    utc_now
)
from typing import Optional
from pathlib import Path
from urllib.parse import urlparse, urljoin
from crawler_1 import fetch_pages
from collections import deque


 
@dataclass
class CrawlerConfig:
    """
    It helps us to pass too many parameters and helps us to initailze easily.
    """
    start_url: str
    output_dir: 'crawl_output'
    max_depth: int = 3
    max_pages: int = 200
    concurrency: int = 20
    delay_seconds: float = 0.0
    timeout_seconds: float = 20.0
    max_bytes: int = 5_000_000
    same_host_only: bool = True
    respect_robots: bool = False
    user_agent: str = 'AtomCrawler/1.0'
    retries: int = 2
    retry_base_delay: False = 1.0
    allowed_content_types: set[str] = field(default_factory=lambda: {
        "text/html",
        "text/plain",
        "application/json",
        "application/xml",
    })


class BFSCrawler:
    """
    A BFSCrawler for Parsing and Extracting links with depth tracking .
    """
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.start_url = normalize_url(config.start_url)
        if not self.start_url:
            raise ValueError(f'Invalid Url: {config.start_url}')
        
        self.start_host = url_host(self.start_url)
        self.visited: set[str] = {self.start_url}
        self.frontier: deque[tuple[str, int]] = deque([(self.start_url, 0)])
        self.pages_crawled = 0

        self.output_dir = Path(config.output_dir)
        self.pages_dir = self.output_dir / "pages"
        self.meta_dir = self.output_dir / "meta"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.meta_dir.mkdir(parents=True, exist_ok=True)

        self.pages_jsonl = self.meta_dir / "pages.jsonl"
        self.edges_jsonl = self.meta_dir / "edges.jsonl"
        self.errors_jsonl = self.meta_dir / "errors.jsonl"
        
        # Reset files for a fresh crawl. 
        for path in [self.pages_jsonl, self.edges_jsonl, self.errors_jsonl]:
            path.write_text("", encoding="utf-8")
        
    def _same_scope(self, url: str) -> bool:
        if not self.config.same_host_only:
            return True
        return url_host(url) == self.start_host

    async def _fetch_once(self, session: aiohttp.ClientSession, url:str) -> dict:
        headers = {"User-Agent": self.config.user_agent}
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)

        async with session.get(url, headers=headers, timeout=timeout, allowed_redirects=True) as resp:
            content_type = content_type_from_headers(dict(resp.headers))
            
            raw = await resp.content.read(self.config.max_bytes)
            truncated = not resp.content.at_eof() 

        return {
            "ok": True,
            "status": resp.status,
            "url": url,
            "final_url": str(resp.url),
            "headers": dict(resp.headers),
            "content_type": content_type,
            "body": raw,
            "truncated": truncated,
        }
    
    # Retry with exponential backoff because some sites
    # temporarily rate limit burst traffic.
    async def _fetch_with_retries(self, session: aiohttp.ClientSession, url: str) -> dict:
        last_error: Optional[str] = None

        for attempt in range(self.config.retries + 1):
            try:
                result = await self._fetch_once(session, url)
                return result
            except Exception as e:
                last_error = repr(e)
                if attemt < self.config.retries:
                    backoff = self.config.retry_base_delay * (2 ** attempt)
                    backoff += random.uniform(0, 0.25)
                    await asyncio.sleep(backoff)
        return {
            "ok": False,
            "status": None,
            "url": url,
            "final_url": url,
            "headers": {},
            "content_type": "",
            "body": b"",
            "truncated": False,
            "error": last_error or "uknown_error",
        }

    # we needed this to figure out way to save different output in different file
    def _save_bytes(self, url: str, body: bytes, content_type: str) -> str:
        ext = guess_extension(content_type)
        # make a file name based on the url and it's content ty
        filename = safe_filename_from_url(url, ext) 
        path = self.pages_dir / filename
        path.write_bytes(body)
        return str(path)
    
    def _append_jsonl(self, path: Path, obj: dict) -> None:
        with path.open('a', encoding='utf-8') as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    
    # Normalize the outgoing Urls because the Urls normally contains fragment(#data)
    # But usually they are for user-interactions it's has no use for crawlers
    def _normalize_outgoing_links(self, links: set[str], base_url: str) -> list[str]:
        out: list[str] = []
        for link in links:
            normalized = normalize_url(link, base=base_url)
            if not normalized:
                continue
            if normalized.startswith('mailto:') or normalized.startswith('javascript:') or normalized.startswith('tel:'):
                continue
            if not self._same_scope(normalized):
                continue
            out.append(normalized)
        return out


    async def crawl(self) -> dict:
        connector = aiohttp.TCPConnector(limit=self.config.concurrency, ssl=False)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)

        summary = {
            "start_url": self.start_url,
            "max_depth": self.config.max_depth,
            "max_pages": self.config.max_pages,
            "pages_crawled": 0,
            "discovered_urls": 1,
            "errors": 0,
        }

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            while self.frontier and self.pages_crawled < self.config.max_pages:
                current_depth = self.frontier[0][1]
                if current_depth > self.config.max_depth:
                    break

                current_url: list[str] = []
                while self.frontier and self.frontier[0][1] == current_depth:
                    url, _ = self.frontier.popleft()
                    current_url.append(url)

                # To limit the Number of concurrent callbacks in the event loop
                sem = asyncio.Semaphore(self.config.concurrency)
                
                tasks = [fetch_pages(session, url, sem) for url in current_url]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for item in results:
                    if isinstance(item, Exception):
                        self._append_jsonl(self.errors_jsonl, {
                            "timestamp": utc_now(),
                            "depth": current_depth,
                            "ok": False,
                            "error": repr(item),
                        })
                        summary["errors"] += 1
                        continue
                    
                    self.pages_crawled += 1

                    for child in item:
                        if self.pages_crawled >= self.config.max_pages:
                            break
                        if child not in self.visited:
                            self.visited.add(child)
                            self.frontier.append((child, current_depth + 1))
                            self._append_jsonl(self.edges_jsonl, {
                                "timestamp": utc_now(),
                                "parent": url,
                                "child": child,
                                "parent_depth": current_depth,
                                "child_depth": current_depth + 1,
                            })
                    summary["pages_crawled"] = self.pages_crawled
                    summary["discovered_urls"] = len(self.visited)
                
            summary["finished_at"] = utc_now()
            summary_path = self.meta_dir / "summary.json"
            summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
            return summary


async def main():
    config = CrawlerConfig(
        start_url="https://techcrunch.com",
        output_dir="crawl_output",
        max_depth=3,
        max_pages=200,
        concurrency=20,
        delay_seconds=0.1,
        timeout_seconds=20,
        respect_robots=False,
        same_host_only=False,
    )

    crawler = BFSCrawler(config)
    summary = await crawler.crawl()
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
