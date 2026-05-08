# Async Web Crawler and Graph Engine( Mainly a prototype) . 

An async web crawler prototype built using only Python's standard library.
The crawler starts from a seed URL, fetches the page, extracts links, and continues crawling using BFS (Breadth First Search) for depth tracking.

## This project was mainly made to understand:
- asynchronous networking(still more to learn)
- graph traversal
- crawling strategies
- queue management
- link extraction pipelines

## Features
- Async crawling
- BFS based traversal
- Depth tracking
- Link extraction
- Graph-like crawl expansion
- Built completely with Python standard library

## How it Works
1. Start with a seed URL
2. Fetch page content asynchronously
3. Parse and extract links
4. Push discovered links into queue
5. Traverse level by level using BFS
6. Track visited URLs and crawl depth

## Example


Seed URL -> Parse Links -> Queue Links -> BFS Crawl

## Things planned:
1. proper rate limiting
2. custom HTML parser
3. retry and backoff logic
4. better error handling
5. robots.txt support
6. concurrent worker management
7. graph visualization
8. persistent storage
