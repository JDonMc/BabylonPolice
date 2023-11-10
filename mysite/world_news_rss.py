import requests
import time


import feedparser
from requests import get





base = ""
urls = ["http://feeds.bbci.co.uk/news/world/rss.xml", "http://www.aljazeera.com/xml/rss/all.xml", 
    "http://rss.cnn.com/rss/edition_world.rss", 
    "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", 
    "https://www.cnbc.com/id/100727362/device/rss/rss.html", 
    "https://feeds.washingtonpost.com/rss/world", "https://www.rt.com/rss/news/", 
    "http://abcnews.go.com/abcnews/internationalheadlines", 
    "https://feeds.feedburner.com/ndtvnews-world-news", "http://www.npr.org/rss/rss.php", 
    "https://www.thesun.co.uk/news/worldnews/feed/", "http://feeds.feedburner.com/daily-express-world-news", 
    "https://time.com/feed/", "http://www.smh.com.au/rssheadlines/world/article/rss.xml", 
    "https://www.france24.com/en/rss", "https://www.ctvnews.ca/rss/world/ctvnews-ca-world-public-rss-1.822289", 
    "http://www.channelnewsasia.com/rssfeeds/8395884", "http://feeds.news24.com/articles/news24/World/rss", 
    "https://www.rawstory.com/category/world/feed/", "https://www.seattletimes.com/nation-world/world/feed/", 
    "http://www.thestar.com/content/thestar/feed.RSSManagerServlet.articles.news.world.rss", 
    "https://www.dailytelegraph.com.au/news/world/rss", "http://ifpnews.com/feed", 
    "https://247newsaroundtheworld.com/feed/", "https://dailyresearchplot.com/feed/", 
    "https://insidexpress.com/feed/", "https://www.easternherald.com/feed/", 
    "https://www.watchdoguganda.com/feed", "https://www.headlinesoftoday.com/feed", 
    "https://worldnewsera.com/feed/", "https://internewscast.com/feed/", "https://wowplus.net/feed/", 
    "https://www.theunionjournal.com/feed/", "https://radarr.africa/feed/", 
    "https://www.thenexthint.com/feed/", "http://feeds.feedburner.com/WarNewsUpdates", 
    "https://newslanes.com/feed/", "https://statehooddc.com/feed/", "https://www.usnn.news/feed/", 
    "https://www.scmp.com/rss/91/feed", "http://www.independent.co.uk/news/world/rss", 
    "https://www.abc.net.au/news/feed/52278/rss.xml", "http://www.mirror.co.uk/news/world-news/rss.xml", 
    "https://3-mob.com/feed/", "https://www.reporter.am/feed/", "https://feeds.breakingnews.ie/bnworld"]


for rss_url in urls:
    xml = base + rss_url

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    feed = feedparser.parse(xml)
    # Print out feed meta data
    #print(feed.feed.title_detail.language)
    
    # Iteratively print feed items
    for item in feed.entries:
        print(item.title)
        print(item.summary)
        
        r = requests.post('https://www.predictionary.us/B/posts/',data={'title':item.title, "body":item.summary, "url": item.link})
        print(r.status_code)
        print(r.text)

        




