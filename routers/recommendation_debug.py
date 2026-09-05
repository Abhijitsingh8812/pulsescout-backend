from fastapi import APIRouter

from services.recommendation_service import (
    get_recommendations
)

router = APIRouter()


@router.get(
    "/recommendation-debug"
)
def recommendation_debug(
    user_id: str
):

    articles = (
        get_recommendations(
            user_id,
            limit=20
        )
    )

    return {

        "count": len(
            articles
        ),

        "articles": articles
    }