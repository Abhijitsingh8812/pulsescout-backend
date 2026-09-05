from services.discovery_registry import DISCOVERY_RSS
from services.rss_fetcher import fetch_rss
from services.deduplicator import deduplicate
from services.cache_service import get_cache, set_cache

DISCOVERY_CACHE_KEY = "discovery"


def get_discovery_news():

    cached = get_cache(
        DISCOVERY_CACHE_KEY
    )

    if cached:

        print(
            "CACHE HIT: DISCOVERY"
        )

        return cached

    print(
        "CACHE MISS: DISCOVERY"
    )

    articles = []

    for feed_type, url in DISCOVERY_RSS.items():

        feed_articles = fetch_rss(
            url
        )

        for article in feed_articles:

            article["discovery_type"] = (
                feed_type
            )

        articles.extend(
            feed_articles
        )

    articles = deduplicate(
        articles
    )

    articles.sort(
        key=lambda x: x.get(
            "published",
            ""
        ),
        reverse=True
    )

    set_cache(
        DISCOVERY_CACHE_KEY,
        articles
    )

    return articles