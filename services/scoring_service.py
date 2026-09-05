from services.trending_service import (
    get_trending_score
)

from services.freshness_service import (
    freshness_score
)


def score_article(
    article,
    profile
):

    score = 0

    title = (
        article.get(
            "title",
            ""
        ).lower()
    )

    for topic, weight in profile.items():

        if topic.lower() in title:

            score += weight

    trending = get_trending_score(
        article["url"]
    )

    freshness = freshness_score(
        article["published_at"]
    )

    score += trending

    score += freshness

    return score