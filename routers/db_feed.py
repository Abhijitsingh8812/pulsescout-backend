from fastapi import APIRouter

from services.news_db_service import (
    get_news
)

router = APIRouter()


@router.get("/db/global/{category}")
def global_feed(category: str):

    articles = get_news(
        "global",
        category
    )

    return {
        "region": "global",
        "category": category,
        "count": len(articles),
        "articles": articles
    }


@router.get("/db/india/{category}")
def india_feed(category: str):

    articles = get_news(
        "india",
        category
    )

    return {
        "region": "india",
        "category": category,
        "count": len(articles),
        "articles": articles
    }