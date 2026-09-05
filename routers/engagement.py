from typing import Optional
from fastapi import APIRouter, Depends

from core.security import get_optional_user
from services.like_service import (
    like_article
)
from services.share_service import (
    share_article
)

router = APIRouter()


@router.post("/like")
def like(
    article_url: str,
    topic: str,
    user_id: Optional[str] = None,
    user: Optional[dict] = Depends(get_optional_user)
):
    effective_user_id = user["uid"] if user else (user_id or "guest")

    like_article(
        effective_user_id,
        article_url,
        topic
    )

    return {
        "status": "liked"
    }


@router.post("/share")
def share(
    article_url: str,
    topic: str,
    user_id: Optional[str] = None,
    user: Optional[dict] = Depends(get_optional_user)
):
    effective_user_id = user["uid"] if user else (user_id or "guest")

    share_article(
        effective_user_id,
        article_url,
        topic
    )

    return {
        "status": "shared"
    }