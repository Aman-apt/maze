import os
import aiohttp
import asyncio
import asyncpg
from pathlib import Path
from bs4 import BeautifulSoup
from collections import deque 
from dotenv import load_dotenv


pool: asyncpg.Pool = None
load_dotenv()

# Note: Work on this later. It's for psql.
async def create_db_pool():
    global pool
    pool = await asyncpg.create_pool(
        dsn=os.getenv('DATABASE_URL'),
        min_size=2,
        max_size=10 
    )


async def fetch_pages(session: aiohttp.ClientSession, seed_url: str, semaphore: asyncio.Semaphore, max_retries=3) -> set[str]:
    """
    Fetch pages, parse HTML, and return a set of discovered links.
    """
    discovered_links = set()
    timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=20)

    for attempt in range(max_retries):
        try:
            async with semaphore:
                async with session.get(seed_url, timeout=timeout) as response:
                    if 200 <= response.status <= 299:
                        html = await response.text()
                        if not html:
                            raise ValueError("Empty response body")

                        soup = BeautifulSoup(html, "html.parser")
                        for tag in soup.find_all("a"):
                            href = tag.get("href")
                            if href and href.startswith("https"):
                                discovered_links.add(href)
                        break
                    else:
                        break 
    
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait = (2 ** attempt) + (attempt * 0.1) 
            if attempt == max_retries - 1:
                return discovered_links
            await asyncio.sleep(wait)
    return discovered_links


async def crawl(seed_url: str, max_depth: int = 3) -> set[str]:

    headers = {
        'User-Agent': (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        )
    }

    # Note: It was really helful to use tuple. 
    frontier: deque[tuple[str, int]] = deque([(seed_url, 0)]) 
    visited: set[str] = {seed_url} 
    # v_links : list[str] = []

    # # Dump the Links to file
    # flat_links = [href for ur in v_links for href in ur]
    # output_file = Path('/home/aman/maze/crawler/links.txt')
    
    # with open(output_file, 'w', encoding='utf-8') as file:
    #     for li in flat_links:
    #         file.write(li + " ".join())
    
    # Note: Never inside the loop.
    semaphore = asyncio.Semaphore(20)

    # A long-lived session, i was creating one-session-per-call and have to torn it down. it was messy
    async with aiohttp.ClientSession(headers=headers) as session:
        while frontier:
            current_depth = frontier[0][1] #it's nested, slipped through my mind

            if current_depth >= max_depth:
                break

            current_url: list[str] = []
            while frontier and frontier[0][1] == current_depth:
                url, _ = frontier.popleft()
                current_url.append(url)
            
            print(f'Current depth: {current_depth}: crawling {len(current_url)} .')

            tasks = [fetch_pages(session, url, semaphore) for url in current_url]
            results = await asyncio.gather(*tasks, return_exceptions=True) 

            for result in results:
                if isinstance(result, Exception):
                    print(f'Task Error: {result}')
                    continue

                for link in result:
                    if link not in visited:
                        v_links.append(link)
                        visited.add(link)
                        frontier.append((link, current_depth + 1))

            print(f"Crawl complete. {len(visited)} unique URLs discovered.")
    # print(v_links)
    return v_links


# async def fetch_to_json(file_path: str) -> None:
#     seed = 'https://techrcunch.com'
#     crawler = await crawl(seed)
#     path = Path('/home/aman/maze/crawler/links.json')
#     with open(path, 'w') as file:
#         for line in crawler:
#             file.write(line)
#     return crawler

 
async def main():
    # await create_db()
    # we'll use databse for the next version this was a prototype.
    
    http = 'https://techcrunch.com'
    crawled_data = await crawl(http)
    print(type(crawled_data))
    output_file = Path("/home/aman/maze/crawler/links.txt")

    with open(output_file, "w", encoding="utf-8") as file:
        for link in crawled_data:
            file.write(link + "\n")
    

if __name__ == '__main__':
    asyncio.run(main())