from pydantic import BaseModel

class Article(BaseModel):
    title: str
    source: str
    url: str
    published_at: str
    image_url: str | None = None