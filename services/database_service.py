import os
from bs4 import BeautifulSoup
from core.db import execute_query, execute_batch, get_db_connection


def clean_html(text):
    if not text:
        return ""

    try:
        return BeautifulSoup(
            text,
            "html.parser"
        ).get_text(
            separator=" ",
            strip=True
        )
    except Exception:
        return text


def save_articles_batch(articles_list, region, category):
    if not articles_list:
        return 0

    records = []
    seen_urls = set()

    for article in articles_list:
        article_url = article.get("link") or article.get("url") or ""
        if not article_url or article_url in seen_urls:
            continue
        seen_urls.add(article_url)

        records.append((
            clean_html(article.get("title", "")),
            clean_html(article.get("summary", "")),
            article.get("source", ""),
            article_url,
            article.get("image_url", ""),
            article.get("published", ""),
            region,
            category
        ))

    if not records:
        return 0

    sql = """
        INSERT INTO articles (title, summary, source, url, image_url, published_at, region, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
    """

    try:
        saved_count = execute_batch(sql, records)
        print(f"[BATCH UPSERT] Processed {saved_count} articles for {region}/{category}")
        return saved_count
    except Exception as e:
        print(f"[BATCH UPSERT ERROR] {region}/{category}: {e}")
        return 0


def save_article(article, region, category):
    return save_articles_batch([article], region, category) > 0


def get_articles_by_region_and_category(
    region: str,
    category: str,
    limit: int = 20
):
    try:
        sql = """
            SELECT * FROM articles
            WHERE region = %s AND category = %s
            ORDER BY created_at DESC
            LIMIT %s;
        """
        return execute_query(sql, (region, category, limit))
    except Exception as e:
        print(f"GET ARTICLES ERROR: {e}")
        return []


def get_articles_by_region_and_categories(
    region: str,
    categories: list[str],
    limit: int = 100
):
    if not categories:
        return []
    try:
        sql = """
            SELECT * FROM articles
            WHERE region = %s AND category = ANY(%s)
            ORDER BY created_at DESC
            LIMIT %s;
        """
        return execute_query(sql, (region, categories, limit))
    except Exception as e:
        print(f"GET TOP ARTICLES ERROR: {e}")
        return []


def get_articles_by_category(
    category: str,
    limit: int = 20
):
    try:
        sql = """
            SELECT * FROM articles
            WHERE category = %s
            ORDER BY created_at DESC
            LIMIT %s;
        """
        return execute_query(sql, (category, limit))
    except Exception as e:
        print(f"GET CATEGORY ERROR: {e}")
        return []


def get_articles_by_region(
    region: str,
    limit: int = 20
):
    try:
        sql = """
            SELECT * FROM articles
            WHERE region = %s
            ORDER BY created_at DESC
            LIMIT %s;
        """
        return execute_query(sql, (region, limit))
    except Exception as e:
        print(f"GET REGION ERROR: {e}")
        return []


def get_latest_articles(limit: int = 20):
    try:
        sql = """
            SELECT * FROM articles
            ORDER BY created_at DESC
            LIMIT %s;
        """
        return execute_query(sql, (limit,))
    except Exception as e:
        print(f"LATEST ARTICLES ERROR: {e}")
        return []
