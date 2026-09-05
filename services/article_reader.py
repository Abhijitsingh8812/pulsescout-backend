# services/article_reader.py

from newspaper import Article


def extract_article(url: str):

    try:

        article = Article(url)

        article.download()

        article.parse()

        return {
            "title": article.title,
            "content": article.text,
            "authors": article.authors,
            "top_image": article.top_image
        }

    except Exception as e:

        print("ARTICLE ERROR:", e)

        return {
            "title": "",
            "content": "",
            "authors": [],
            "top_image": ""
        }