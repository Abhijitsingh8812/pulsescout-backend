from core.db import execute_query
from services.user_service import get_preferences
from services.interest_service import get_top_interests
from services.ranking_service import calculate_score


def get_recommendations(
    user_id,
    limit=50
):
    categories = []
    interest_lookup = {}

    prefs = get_preferences(user_id)
    if prefs:
        categories = prefs.get("preferred_categories", []) or []

    interests = get_top_interests(user_id)
    for item in interests:
        interest_lookup[item["category"]] = item["score"]

    if not categories:
        categories = [item["category"] for item in interests if item.get("category")]

    if not categories:
        return []

    try:
        sql_articles = "SELECT * FROM articles WHERE category = ANY(%s) LIMIT 200;"
        articles = execute_query(sql_articles, (categories,))

        if not articles:
            return []

        urls = [a["url"] for a in articles if a.get("url")]
        metrics_lookup = {}
        if urls:
            sql_metrics = "SELECT * FROM article_metrics WHERE article_url = ANY(%s);"
            metrics_rows = execute_query(sql_metrics, (urls,))
            for m in metrics_rows:
                metrics_lookup[m["article_url"]] = m

        for article in articles:
            category = article.get("category", "")
            interest_score = interest_lookup.get(category, 0)
            
            metric_row = metrics_lookup.get(article.get("url"), {})
            trending_score = (
                (metric_row.get("views") or 0)
                + (metric_row.get("bookmarks") or 0) * 2
                + (metric_row.get("shares") or 0) * 3
            )

            article["recommendation_score"] = calculate_score(
                article,
                interest_score,
                trending_score
            )

        articles.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
        return articles[:limit]
    except Exception as e:
        print(f"GET RECOMMENDATIONS ERROR: {e}")
        return []