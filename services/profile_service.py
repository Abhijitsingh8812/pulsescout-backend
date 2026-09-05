from core.db import execute_query


def get_user_profile(
    user_id: str
):
    profile = {}
    if not user_id:
        return profile

    try:
        sql = "SELECT topic, score FROM user_topics WHERE user_id = %s;"
        rows = execute_query(sql, (user_id,))
        for row in rows:
            profile[row["topic"]] = row["score"]
        return profile
    except Exception as e:
        print(f"PROFILE FETCH ERROR: {e}")
        return profile