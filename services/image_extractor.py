# services/image_extractor.py

from newspaper import Article


def extract_article_image(url: str):

    try:

        article = Article(url)

        article.download()

        article.parse()

        return article.top_image

    except Exception:

        return ""