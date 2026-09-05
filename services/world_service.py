import feedparser

from services.world_registry import WORLD_RSS
from services.world_mapping import WORLD_CATEGORIES
from services.text_cleaner import clean_html


def get_world_category(category: str):

    category = category.lower()

    if category not in WORLD_CATEGORIES:
        return []

    feeds = WORLD_CATEGORIES[category]

    articles = []

    for feed_key in feeds:

        if feed_key not in WORLD_RSS:
            continue

        feed_url = WORLD_RSS[feed_key]

        try:

            feed = feedparser.parse(
                feed_url
            )

            for entry in feed.entries:

                raw_summary = (
                    entry.get("summary")
                    or entry.get("description")
                    or ""
                )

                summary = clean_html(
                    raw_summary
                )[:300]

                articles.append({

                    "title": entry.get(
                        "title",
                        ""
                    ),

                    "link": entry.get(
                        "link",
                        ""
                    ),

                    "summary": summary,

                    "source": feed_key
                })

        except Exception as e:

            print(
                f"WORLD FEED ERROR: {feed_key}"
            )

            print(
                f"ERROR: {e}"
            )

            continue

    return articles