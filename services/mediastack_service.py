import os
import requests

MEDIASTACK_API = os.getenv("MEDIASTACK_API")


def search_mediastack(query):

    print("MEDIASTACK CALLED")

    url = (
        f"http://api.mediastack.com/v1/news"
        f"?access_key={MEDIASTACK_API}"
        f"&keywords={query}"
        f"&languages=en"
        f"&limit=100"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data.get("data", []):

        articles.append({
    "title": article.get("title"),
    "description": article.get("description"),
    "url": article.get("url"),
    "image_url": article.get("image"),
    "source": "MediaStack"
})

    return articles