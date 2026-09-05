from fastapi import APIRouter

from services.database_service import (
    get_articles_by_region_and_categories
)

router = APIRouter()

TOP_CATEGORIES = [
    "business",
    "technology",
    "politics",
    "sports",
    "world"
]


@router.get("/top/india")
def top_india_news():
    articles = get_articles_by_region_and_categories(
        region="india",
        categories=TOP_CATEGORIES,
        limit=100
    )

    return {
        "region": "india",
        "count": len(articles),
        "articles": articles
    }


@router.get("/top/global")
def top_global_news():
    articles = get_articles_by_region_and_categories(
        region="global",
        categories=TOP_CATEGORIES,
        limit=100
    )

    return {
        "region": "global",
        "count": len(articles),
        "articles": articles
    }