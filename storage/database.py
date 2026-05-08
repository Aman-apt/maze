import aiohttp
import asyncpg

async def get_connection():
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="amanCrawler",
        password="amanonlinux",
        database="crawlerDb"
    )
    return conn