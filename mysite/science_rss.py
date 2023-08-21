import requests
import time


import feedparser
from requests import get

base = "http://export.arxiv.org/rss/"
urls = ["https://www.newscientist.com/feed/home/?cmpid=RSS%7CNSNS-Home", "https://www.nytimes.com/svc/collections/v1/publish/http://www.nytimes.com/section/science/rss.xml", "https://www.forbes.com/science/feed2/", "https://news.climate.columbia.edu/feed/", "http://feeds.feedburner.com/sciencealert-latestnews", "https://www.sciencedaily.com/rss/", "http://www.space.com/feeds/all", "https://phys.org/rss-feed/chemistry-news/", "https://scitechdaily.com/feed/", "https://wattsupwiththat.com/feed/", "https://www.zmescience.com/feed/", "http://www.realclearscience.com/index.xml", "http://www.futurity.org/feed/", "https://knowridge.com/feed/", "https://scientificinquirer.com/feed/"]


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





