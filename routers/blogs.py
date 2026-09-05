from fastapi import APIRouter

from services.blogs_service import (
    get_blog_category
)

router = APIRouter()


@router.get("/blogs/{category}")
def blogs(category: str):

    articles = get_blog_category(
        category
    )

    return {

        "category": category,

        "count": len(articles),

        "articles": articles
    }