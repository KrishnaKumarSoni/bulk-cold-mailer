import requests
from bs4 import BeautifulSoup
import logging

def scrape_company_info(url):
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return text
    except requests.RequestException as e:
        logging.error(f"Error: {e} for URL: {url}")
        return ""
