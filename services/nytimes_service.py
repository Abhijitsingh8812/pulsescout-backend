import os
import requests

DEVELOPER_NY_TIMES_API = os.getenv("DEVELOPER_NY_TIMES_API")


def search_nytimes(query):

    print("NYTIMES CALLED")

    url = (
        f"https://api.nytimes.com/svc/search/v2/articlesearch.json"
        f"?q={query}"
        f"&api-key={DEVELOPER_NY_TIMES_API}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    docs = data.get("response", {}).get("docs", [])

    for article in docs:

        image_url = None

        multimedia = article.get("multimedia", [])

        if multimedia:
            image_url = (
                "https://www.nytimes.com/"
                + multimedia[0].get("url", "")
            )

        articles.append({
            "title": article.get("headline", {}).get("main"),
            "description": article.get("abstract"),
            "url": article.get("web_url"),
            "image_url": image_url,
            "source": "NYTimes"
        })

    return articles