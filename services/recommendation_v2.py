from core.db import execute_query
from services.profile_service import get_user_profile
from services.scoring_service import score_article


def get_personalized_feed(
    user_id: str
):
    profile = get_user_profile(user_id)

    try:
        sql = "SELECT * FROM articles ORDER BY created_at DESC LIMIT 200;"
        articles = execute_query(sql)

        if not articles:
            return []

        ranked = []
        for article in articles:
            score = score_article(article, profile)
            article["recommendation_score"] = score
            ranked.append(article)

        ranked.sort(
            key=lambda x: x.get("recommendation_score", 0),
            reverse=True
        )

        return ranked[:100]
    except Exception as e:
        print(f"GET PERSONALIZED FEED ERROR: {e}")
        return []