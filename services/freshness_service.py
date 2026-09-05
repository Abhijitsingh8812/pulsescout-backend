from datetime import datetime
from dateutil import parser


def freshness_score(
    published_at
):

    try:

        published = parser.parse(
            published_at
        )

        age_seconds = (
            datetime.utcnow()
            -
            published.replace(
                tzinfo=None
            )
        ).total_seconds()

        hours = age_seconds / 3600

        if hours < 1:
            return 20

        if hours < 6:
            return 15

        if hours < 24:
            return 10

        if hours < 48:
            return 5

        return 1

    except Exception:

        return 0