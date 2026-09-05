from datetime import datetime
from dateutil.parser import parse


def calculate_freshness_score(
    published_at
):

    try:

        article_time = parse(
            published_at
        )

        hours = (
            datetime.utcnow() -
            article_time.replace(
                tzinfo=None
            )
        ).total_seconds() / 3600

        if hours <= 1:
            return 30

        elif hours <= 6:
            return 20

        elif hours <= 24:
            return 10

        return 2

    except Exception:

        return 0


def calculate_score(
    article,
    interest_score=0,
    trending_score=0
):

    freshness_score = (
        calculate_freshness_score(
            article.get(
                "published_at",
                ""
            )
        )
    )

    total_score = (

        interest_score * 0.5 +

        trending_score * 0.3 +

        freshness_score * 0.2
    )

    return total_score