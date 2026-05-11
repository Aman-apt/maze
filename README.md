# Async Web Crawler and Graph Engine( Mainly a prototype) . 

An async web crawler prototype built using only Python's standard library.
The crawler starts from a seed URL, fetches the page, extracts links, and continues crawling using BFS (Breadth First Search) for depth tracking.

## This project was mainly made to understand:
- asynchronous networking
- graph traversal(not implemented it yet .)
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
![Crawl Output](screenshot/output.png)
![Crawl Output](screenshot/cli_output.png)


Seed URL -> Parse Links -> Queue Links -> BFS Crawl

## Examples of Version-2:
{"timestamp": "2026-05-11T03:56:24.316640+00:00", "parent": "https://www.reddit.com/submit?url=https%3A%2F%2Ftechcrunch.com%2F2026%2F05%2F08%2Fpoland-says-hackers-breached-water-treatment-plants-and-the-u-s-is-facing-the-same-threat%2F&title=Poland+says+hackers+breached+water+treatment+plants%2C+and+the+US+is+facing+the+same+threat", "child": "https://www.youtube.com/watch?v=etjXG25vPUk&t=48s", "parent_depth": 2, "child_depth": 3}
{"timestamp": "2026-05-11T03:56:24.316662+00:00", "parent": "https://www.reddit.com/submit?url=https%3A%2F%2Ftechcrunch.com%2F2026%2F05%2F08%2Fpoland-says-hackers-breached-water-treatment-plants-and-the-u-s-is-facing-the-same-threat%2F&title=Poland+says+hackers+breached+water+treatment+plants%2C+and+the+US+is+facing+the+same+threat", "child": "https://www.facebook.com/sharer.php?u=https%3A%2F%2Ftechcrunch.com%2F2025%2F10%2F27%2Ffitbits-revamped-app-with-gemini-powered-health-coach-rolls-out-to-premium-users%2F", "parent_depth": 2, "child_depth": 3}

