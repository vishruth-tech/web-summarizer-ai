import requests
from bs4 import BeautifulSoup

def fetch_website_contents(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.extract()

    # For Wikipedia specifically, remove references and external links sections
    for section in soup.find_all("div", {"class": ["reflist", "mw-references-wrap"]}):
        section.extract()

    text = soup.get_text(separator=" ", strip=True)
    return text