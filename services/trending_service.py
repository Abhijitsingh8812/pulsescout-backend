from core.db import execute_query, execute_one


def get_trending(limit=20):
    try:
        sql_metrics = "SELECT article_url FROM article_metrics ORDER BY views DESC LIMIT %s;"
        metrics = execute_query(sql_metrics, (limit,))

        if not metrics:
            return []

        urls = [m["article_url"] for m in metrics if m.get("article_url")]
        if not urls:
            return []

        sql_articles = "SELECT * FROM articles WHERE url = ANY(%s);"
        return execute_query(sql_articles, (urls,))
    except Exception as e:
        print(f"GET TRENDING ERROR: {e}")
        return []


def get_trending_score(
    article_url
):
    if not article_url:
        return 0
    try:
        sql = "SELECT views, likes, shares FROM article_metrics WHERE article_url = %s LIMIT 1;"
        metric = execute_one(sql, (article_url,))
        if not metric:
            return 0

        return (
            (metric.get("views") or 0)
            + (metric.get("likes") or 0) * 3
            + (metric.get("shares") or 0) * 5
        )
    except Exception as e:
        print(f"GET TRENDING SCORE ERROR: {e}")
        return 0