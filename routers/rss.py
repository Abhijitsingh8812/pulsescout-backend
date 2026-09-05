# routers/rss.py

from fastapi import APIRouter

from services.rss_service import (
    get_india_category,
    get_global_category
)

router = APIRouter(
    tags=["RSS Feeds"]
)


@router.get("/feed/india/{category}")
def india_feed(category: str):

    articles = get_india_category(category)

    return {
        "region": "india",
        "category": category,
        "count": len(articles),
        "articles": articles
    }


@router.get("/feed/global/{category}")
def global_feed(category: str):

    articles = get_global_category(category)

    return {
        "region": "global",
        "category": category,
        "count": len(articles),
        "articles": articles
    }