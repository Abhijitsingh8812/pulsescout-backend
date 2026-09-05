from fastapi import APIRouter

from services.world_service import get_world_category

router = APIRouter(
    prefix="/world",
    tags=["World"]
)


@router.get("/{category}")
def world_news(category: str):

    return {
        "category": category,
        "articles": get_world_category(category)
    }