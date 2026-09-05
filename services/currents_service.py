import os
import requests

CURRENT_NEWS_API = os.getenv("CURRENT_NEWS_API")


def search_currents(query):

    print("CURRENTS CALLED")

    url = (
        f"https://api.currentsapi.services/v1/search"
        f"?keywords={query}"
        f"&apiKey={CURRENT_NEWS_API}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data.get("news", []):

        articles.append({
    "title": article.get("title"),
    "description": article.get("description"),
    "url": article.get("url"),
    "image_url": article.get("image"),
    "source": "Currents"
})

    return articles