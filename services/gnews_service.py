import os
import requests

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

def search_gnews(query):

    print("GNEWS CALLED")

    url = (
        f"https://gnews.io/api/v4/search"
        f"?q={query}"
        f"&apikey={GNEWS_API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data.get("articles", []):

        articles.append({
    "title": article.get("title"),
    "description": article.get("description"),
    "url": article.get("url"),
    "image_url": article.get("image"),
    "source": "GNews"
})

    return articles