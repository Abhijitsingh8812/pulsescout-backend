# services/rss_fetcher.py

import feedparser

from services.image_extractor import extract_article_image
from services.text_cleaner import clean_html


def extract_image(entry):
    """
    Extract image directly from RSS feed if available.
    """

    try:

        if "media_content" in entry:

            media = entry.media_content

            if media and len(media) > 0:

                return media[0].get(
                    "url",
                    ""
                )

        if "media_thumbnail" in entry:

            thumbnail = entry.media_thumbnail

            if thumbnail and len(thumbnail) > 0:

                return thumbnail[0].get(
                    "url",
                    ""
                )

        if "enclosures" in entry:

            enclosure = entry.enclosures

            if enclosure and len(enclosure) > 0:

                return enclosure[0].get(
                    "href",
                    ""
                )

        return ""

    except Exception as e:

        print(
            f"IMAGE EXTRACTION ERROR: {e}"
        )

        return ""


def fetch_rss(url: str):

    try:

        print("=" * 60)

        print(
            f"FETCHING RSS: {url}"
        )

        feed = feedparser.parse(
            url
        )

        feed_title = feed.feed.get(
            "title",
            "Unknown Source"
        )

        print(
            f"FEED TITLE: {feed_title}"
        )

        print(
            f"TOTAL ENTRIES: {len(feed.entries)}"
        )

        articles = []

        for entry in feed.entries:

            try:

                title = entry.get(
                    "title",
                    ""
                )

                raw_summary = (
                    entry.get("summary")
                    or entry.get("description")
                    or ""
                )

                summary = clean_html(
                    raw_summary
                )[:300]

                link = entry.get(
                    "link",
                    ""
                )

                published = entry.get(
                    "published",
                    ""
                )

                published_parsed = entry.get(
                    "published_parsed"
                )

                image_url = extract_image(
                    entry
                )

                image_url = extract_image(entry)

                # Skip slow HTML image extraction.
                # Only use images provided by the RSS feed.
                image_url = image_url or ""
                article = {

                    "title": title,

                    "summary": summary,

                    "link": link,

                    "published": published,

                    "published_parsed": published_parsed,

                    "source": feed_title,

                    "image_url": image_url
                }

                articles.append(
                    article
                )

            except Exception as article_error:

                print(
                    f"ARTICLE PROCESSING ERROR: {article_error}"
                )

                continue

        print(
            f"SUCCESS: {feed_title} -> {len(articles)} articles"
        )

        return articles

    except Exception as e:

        print("=" * 60)

        print(
            "RSS FETCH ERROR"
        )

        print(
            f"URL: {url}"
        )

        print(
            f"ERROR: {e}"
        )

        print("=" * 60)

        return []