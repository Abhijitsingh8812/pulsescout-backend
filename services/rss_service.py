from services.rss_registry import (
    INDIA_RSS,
    GLOBAL_RSS,
    INDIA_DYNAMIC_RSS,
    GLOBAL_DYNAMIC_RSS
)
from services.category_mapping import (
    INDIA_CATEGORIES,
    GLOBAL_CATEGORIES
)
from services.rss_fetcher import fetch_rss
from services.deduplicator import deduplicate
from services.cache_service import get_cache, set_cache
from services.database_service import save_article, save_articles_batch
from services.text_cleaner import clean_html


def _process(region, category, feeds_map_static, feeds_map_dynamic, category_map):
    cache_key = f"{region}_{category}"

    cached = get_cache(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return cached

    print(f"CACHE MISS: {cache_key}")

    articles = []

    for feed_name in category_map.get(category, []):
        try:
            if feed_name in feeds_map_static:
                articles.extend(
                    fetch_rss(feeds_map_static[feed_name])
                )

            elif feed_name in feeds_map_dynamic:
                articles.extend(
                    fetch_rss(feeds_map_dynamic[feed_name])
                )

        except Exception as e:
            print(f"RSS ERROR ({feed_name}): {e}")

    articles = deduplicate(articles)

    articles.sort(
        key=lambda x: x.get("published_parsed") or (0,),
        reverse=True
    )

    cleaned = []

    for article in articles:
        try:
            article["summary"] = clean_html(
                article.get("summary", "")
            )[:300]
            cleaned.append(article)
        except Exception as e:
            print(f"ARTICLE PROCESS ERROR: {e}")

    # Save articles in a single bulk operation per category
    if cleaned:
        save_articles_batch(cleaned, region, category)

    set_cache(
        cache_key,
        cleaned
    )

    return cleaned



def get_india_category(category: str):
    return _process(
        "india",
        category,
        INDIA_RSS,
        INDIA_DYNAMIC_RSS,
        INDIA_CATEGORIES
    )


def get_global_category(category: str):
    return _process(
        "global",
        category,
        GLOBAL_RSS,
        GLOBAL_DYNAMIC_RSS,
        GLOBAL_CATEGORIES
    )