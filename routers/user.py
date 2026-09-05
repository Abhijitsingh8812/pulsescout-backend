from fastapi import APIRouter, Depends

from core.security import get_current_user
from services.user_service import (
    save_preferences,
    get_preferences
)

router = APIRouter()


@router.post("/users/preferences")
def update_preferences(
    categories: list[str],
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    success = save_preferences(
        user_id,
        categories
    )

    return {
        "success": success
    }


@router.get("/users/preferences")
def fetch_preferences(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    return get_preferences(
        user_id
    )