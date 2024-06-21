import requests
import time


import feedparser
from requests import get

base = "http://export.arxiv.org/rss/"
urls = ["https://bookriot.com/feed/", "https://www.kirkusreviews.com/feeds/rss/", "https://cointelegraph.com/rss", "https://bitcoinist.com/feed/", "https://www.newsbtc.com/feed/", "https://www.coinspeaker.com/news/feed/",
"https://cryptopotato.com/feed/", "https://crypto.news/feed/"]


for rss_url in urls:
    xml = rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    print(feed.feed.title_detail.language)
    
    # Iteratively print feed items
    for item in feed.entries:
        print(item.title)
        print(item.summary)
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url": item.links[0].href})
        print(r.status_code)
        print(r.text)





