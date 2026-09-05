from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from core.security import get_current_user
from services.bookmark_service import (
    save_bookmark,
    remove_bookmark,
    get_user_bookmarks,
    is_bookmarked
)

router = APIRouter(
    tags=["Bookmarks"]
)


class BookmarkRequest(BaseModel):
    user_id: str = ""
    article_url: str
    title: str = ""
    description: str = ""
    image_url: str = ""
    source: str = ""


@router.post("/bookmark")
def bookmark_article(
    payload: BookmarkRequest,
    current_user: dict = Depends(get_current_user)
):
    # Use authoritative UID from verified Firebase token
    verified_uid = current_user["uid"]

    success = save_bookmark(
        user_id=verified_uid,
        article_url=payload.article_url,
        title=payload.title,
        description=payload.description,
        image_url=payload.image_url,
        source=payload.source
    )

    return {
        "success": success
    }


@router.delete("/bookmark")
def delete_bookmark(
    article_url: str,
    user_id: str = "",
    current_user: dict = Depends(get_current_user)
):
    verified_uid = current_user["uid"]

    success = remove_bookmark(
        user_id=verified_uid,
        article_url=article_url
    )

    return {
        "success": success
    }


@router.get("/bookmarks/{user_id}")
def bookmarks(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    verified_uid = current_user["uid"]
    if user_id and user_id != verified_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access bookmarks of another user."
        )

    return get_user_bookmarks(verified_uid)


@router.get("/bookmark/check")
def bookmark_check(
    article_url: str,
    user_id: str = "",
    current_user: dict = Depends(get_current_user)
):
    verified_uid = current_user["uid"]

    return {
        "bookmarked": is_bookmarked(
            user_id=verified_uid,
            article_url=article_url
        )
    }