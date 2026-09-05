from services.newsapi_service import search_newsapi
from services.gnews_service import search_gnews
from services.newsdata_service import search_newsdata
from services.currents_service import search_currents
from services.mediastack_service import search_mediastack
from services.nytimes_service import search_nytimes

from aggregator.dedup import deduplicate_articles


def aggregate_news(query):

    all_articles = []

    # NewsAPI
    try:
        all_articles.extend(
            search_newsapi(query)
        )
    except Exception as e:
        print("NewsAPI Error:", e)

    # GNews
    try:
        all_articles.extend(
            search_gnews(query)
        )
    except Exception as e:
        print("GNews Error:", e)

    # NewsData.io
    try:
        all_articles.extend(
            search_newsdata(query)
        )
    except Exception as e:
        print("NewsData Error:", e)

    # Currents API
    try:
        all_articles.extend(
            search_currents(query)
        )
    except Exception as e:
        print("Currents Error:", e)

    # MediaStack
    try:
        all_articles.extend(
            search_mediastack(query)
        )
    except Exception as e:
        print("MediaStack Error:", e)

    # New York Times
    try:
        all_articles.extend(
            search_nytimes(query)
        )
    except Exception as e:
        print("NYTimes Error:", e)

    print(f"Total articles before dedup: {len(all_articles)}")

    # Remove duplicates
    all_articles = deduplicate_articles(all_articles)

    print(f"Total articles after dedup: {len(all_articles)}")

    return all_articles