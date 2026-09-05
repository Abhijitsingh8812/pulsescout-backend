import os
import requests

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

def search_newsdata(query):

    url = (
        f"https://newsdata.io/api/1/latest"
        f"?apikey={NEWSDATA_API_KEY}"
        f"&q={query}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data.get("results", []):

        articles.append({
    "title": article.get("title"),
    "description": article.get("description"),
    "url": article.get("link"),
    "image_url": article.get("image_url"),
    "source": "NewsData"
})

    return articles