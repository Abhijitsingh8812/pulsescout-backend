from fastapi import APIRouter, Depends

from core.security import get_current_user
from services.topic_service import (
    get_top_topics
)

router = APIRouter()


@router.get("/users/topics")
def user_topics(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    return {
        "user_id": user_id,
        "topics": get_top_topics(
            user_id
        )
    }