from fastapi import APIRouter

from services.discovery_service import (
    get_discovery_news
)

router = APIRouter(
    prefix="/discovery",
    tags=["Discovery"]
)


@router.get("/")
def discovery_feed():

    articles = get_discovery_news()

    return {

        "section": "discovery",

        "count": len(
            articles
        ),

        "articles": articles
    }