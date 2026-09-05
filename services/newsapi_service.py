import os
import requests

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def search_newsapi(query):

    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={query}"
        f"&language=en"
        f"&apiKey={NEWSAPI_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data.get("articles", []):

        articles.append({
    "title": article.get("title"),
    "description": article.get("description"),
    "url": article.get("url"),
    "image_url": article.get("urlToImage"),
    "source": "NewsAPI"
})

    return articles