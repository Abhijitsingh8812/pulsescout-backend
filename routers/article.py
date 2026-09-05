from fastapi import APIRouter
from services.article_reader import extract_article

router = APIRouter(tags=["Article"])

@router.get("/article")
async def get_article(url: str):

    article = extract_article(url)

    return {
        "success": True,
        "article": article
    }