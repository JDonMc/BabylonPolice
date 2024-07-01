import requests
import time


import feedparser
from requests import get











import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = "https://sacredscribesangelnumbers.blogspot.com/p/index-numbers.html"

# Send a request to the URL
response = requests.get(url)
response.raise_for_status()

# Parse the content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the links for angel numbers
links = soup.find_all('a', href=True)

angel_numbers = {}

# Iterate through the links and get the number and description
for link in links:
    number = link.text.strip()
    href = link['href']
    
    if number.isdigit():
        # Request each link
        number_response = requests.get(href)
        number_response.raise_for_status()
        number_soup = BeautifulSoup(number_response.text, 'html.parser')
        
        # Extract the main content (modify as needed to target the right HTML element)
        content = number_soup.find('div', class_='post-body').get_text(separator='\n').strip()
        
        r = requests.post('https://127.0.0.1:8000/B/angel_numbers/',data={'digits':len(str(number)), "numbers":int(number), "description": content})
        


