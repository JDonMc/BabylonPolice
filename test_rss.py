import requests
import time


import feedparser
from requests import get

base = "http://export.arxiv.org/rss/"
urls = ["astro-ph", "cond-mat", "cs", "econ", "eess", "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th", "math", "math-ph", "nlin", "nucl-ex", "nucl-th", "physics", "q-bio", "q-fin", "quant-ph", "stat"]


for rss_url in urls:
    xml = base + rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    print(feed.feed.title_detail.language)
    
    # Iteratively print feed items
    for item in feed.entries:
        print(item)
        print(item.title)
        print(item.links[0].href)
        print(item.summary)
        #r = requests.post('https://www.babylonpolice.com/B/posts/',data={'title':item.title, "body":item.summary, "url": item.link})
        #print(r.status_code)
        #print(r.text)





