from typing import Optional
from fastapi import APIRouter, Depends

from core.security import get_current_user, get_optional_user
from services.metrics_service import (
    increment_view,
    increment_bookmark,
    increment_share
)
from services.interest_service import (
    update_interest,
    get_top_interests
)
from services.topic_service import (
    update_topic
)
from services.topic_extractor import (
    extract_topics
)

router = APIRouter()


@router.post("/view")
def view_article(
    url: str,
    category: str,
    title: str,
    user_id: Optional[str] = None,
    user: Optional[dict] = Depends(get_optional_user)
):
    effective_user_id = user["uid"] if user else (user_id or "guest")

    increment_view(url)

    update_interest(
        effective_user_id,
        category
    )

    topics = extract_topics(
        title
    )

    for topic in topics:
        update_topic(
            effective_user_id,
            topic
        )

    return {
        "success": True,
        "message": "View recorded",
        "topics_found": topics
    }


@router.post("/metrics/bookmark")
def bookmark_article(
    url: str
):
    increment_bookmark(url)
    return {
        "success": True,
        "message": "Bookmark recorded"
    }


@router.post("/share")
def share_article(
    url: str
):
    increment_share(url)
    return {
        "success": True,
        "message": "Share recorded"
    }


@router.get("/users/interests")
def user_interests(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    return {
        "user_id": user_id,
        "interests": get_top_interests(
            user_id
        )
    }