
# import aiohttp
# import asyncio
# from typing import List
# from bs4 import BeautifulSoup
# from collections import deque

# '''
# 1. A queue — your list of "URLs to visit next"
# 2. A visited set — so you don't visit the same URL twice
# 3. A fetcher — downloads the HTML of a URL
# 4. A parser — reads that HTML and finds all the <a href> links
# 5. A saver — writes results somewhere (even just printing to console counts)
# '''
# frontier = deque('https://techrunch.com')
# seed = 'https://techrunch.com'

# async def fetch(url, max_retry=3):

#     pages_list = list()
#     #implement the retry and backoff logic here 
#     for attempt in range(max_retry):
#         if attempt >= max_retry:
#             break
#         else:
#             pass
#         pass 
#     headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/XX.0.0.0 Safari/537.36'}
#     async with aiohttp.ClientSession(headers=headers) as session:
#         try:
#             async with session.get(url, timeout=10) as response:
#                 html = await response.text() #so we have to wait here for data
#                 if not html:
#                     raise ValueError('No response from the server.')
#                 else:
#                     page.append(html)
#         except Exception as e:
#             return("Pages were not found")
#     return page

# # write a better parser for this function  it's not working properly
# async def parser(url): #reads the html and find all the <a href> links

#     return parsed_links

# async def main():
#     data = await parser('https://techrunch.com')
#     print(data)
    
    
# if __name__ == '__main__':
#     asyncio.run(main())

# # so the fetcher is working i am able to download the pages , let's make it 
# # async