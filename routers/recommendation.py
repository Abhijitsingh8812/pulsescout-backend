from fastapi import APIRouter

from services.recommendation_v2 import (
    get_personalized_feed
)

router = APIRouter()


@router.get(
    "/recommendations"
)
def recommendations(
    user_id: str
):

    return get_personalized_feed(
        user_id
    )