from services.blogs_registry import BLOG_RSS
from services.blogs_mapping import BLOG_CATEGORIES

from services.rss_fetcher import fetch_rss
from services.deduplicator import deduplicate


def get_blog_category(category: str):

    articles = []

    feeds = BLOG_CATEGORIES.get(
        category,
        []
    )

    for feed_name in feeds:

        if feed_name in BLOG_RSS:

            articles.extend(
                fetch_rss(
                    BLOG_RSS[feed_name]
                )
            )

    return deduplicate(
        articles
    )