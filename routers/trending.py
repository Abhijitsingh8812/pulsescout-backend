from fastapi import APIRouter

from services.trending_service import (
    get_trending
)

router = APIRouter()


@router.get("/trending")
def trending():

    articles = get_trending()

    return {
        "count": len(articles),
        "articles": articles
    }