import requests
import time


import feedparser
from requests import get

base = "http://export.arxiv.org/rss/"
urls = ["https://www.nytimes.com/services/xml/rss/nyt/HomePage.xml", "https://www.huffpost.com/section/front-page/feed?x=1", "http://rssfeeds.usatoday.com/UsatodaycomNation-TopStories", "http://www.politico.com/rss/politicopicks.xml", "http://www.npr.org/rss/rss.php?id=1001", "https://www.latimes.com/local/rss2.0.xml","https://nypost.com/feed/", "http://feeds.feedburner.com/breitbart", "http://www.newsweek.com/rss", "https://www.chicagotribune.com/rss2.0.xml", "https://www.salon.com/feed", "https://www.boston.com/feed/", "https://www.mercurynews.com/feed/", "https://www.nbcchicago.com/?rss=y", "https://ktla.com/feed/", "http://www.washingtontimes.com/rss/headlines/news/", "https://chicago.suntimes.com/rss/index.xml", "https://abc13.com/feed/", "https://www.kxan.com/feed/", "https://kdvr.com/feed/", "https://gothamist.com/feed", "https://www.kron4.com/feed/", "https://www.bostonherald.com/feed/", "https://abc7news.com/feed/", "https://www.nbcdfw.com/news/feed/", "https://www.nbcwashington.com/?rss=y", "https://www.dailyherald.com/rss/feed/?feed=news_top5", "https://www.phillyvoice.com/feed/", "https://fox5sandiego.com/feed/", "https://fox2now.com/feed/", "https://wsvn.com/feed/", "https://www.twincities.com/feed/", "https://www.nbcmiami.com/?rss=y", "https://www.wivb.com/feed/", "https://whdh.com/feed/", "https://chamberlainsun.com/feed/", "http://timesofsandiego.com/feed/", "https://www.enmnews.com/feed/", "https://lighthome.us/feed/", "https://www.denverpost.com/feed/", "https://wgntv.com/feed/", "https://wtop.com/feed/", "https://www.pe.com/feed/", "https://newrightnetwork.com/feed/"]
urls2 = ["http://feeds.foxnews.com/foxnews/latest"]

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
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url": item.link})
        print(r.status_code)
        print(r.text)

for rss_url in urls2:
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
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url": item.id})
        print(r.status_code)
        print(r.text)



