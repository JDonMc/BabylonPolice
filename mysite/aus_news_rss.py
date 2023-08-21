import requests
import time


import feedparser
from requests import get

base = ""
urls = ["https://www.abc.net.au/news/feed/2942460/rss.xml", "http://www.9news.com.au/rss", "http://www.dailytelegraph.com.au/feed", "http://feeds.smh.com.au/rssheadlines/top.xml", "https://www.news.com.au/feed/", "http://feeds.theage.com.au/rssheadlines/top.xml", "https://www.heraldsun.com.au/rss", "https://www.perthnow.com.au/feed", "http://feeds.brisbanetimes.com.au/rssheadlines/top.xml", "https://www.canberratimes.com.au/rss.xml", "https://www.goldcoastbulletin.com.au/feed", "http://feeds.watoday.com.au/rssheadlines/top.xml", "https://www.townsvillebulletin.com.au/news/rss", "https://www.ntnews.com.au/news/rss", "https://westsidecommunitynews.com.au/feed/", "https://www.theguardian.com/au/rss", "https://www.theaustralian.com.au/feed/", "http://www.huffingtonpost.com.au/rss/index.xml", "https://bestinau.com.au/feed/", "https://tasmaniantimes.com/?/feeds/rss", "https://www.themercury.com.au/feed/", "https://www.northernstar.com.au/feeds/rss/homepage/", "https://www.coffscoastadvocate.com.au/feeds/rss/homepage/"]


for rss_url in urls:
    xml = base + rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    print(feed.feed.title_detail.language)
    
    # Iteratively print feed items
    for item in feed.entries:
        print(item.title)
        print(item.summary)
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url": item.link})
        print(r.status_code)
        print(r.text)





