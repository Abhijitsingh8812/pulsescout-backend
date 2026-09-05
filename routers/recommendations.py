from fastapi import APIRouter, Depends

from core.security import get_current_user
from services.recommendation_v2 import (
    get_personalized_feed
)

router = APIRouter()


@router.get("/recommendations")
def recommendations(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    articles = get_personalized_feed(
        user_id
    )

    return {
        "count": len(articles),
        "articles": articles
    }