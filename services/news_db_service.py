from core.db import execute_query


def get_news(
    region: str,
    category: str,
    limit: int = 100
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
        print(f"GET NEWS DB ERROR: {e}")
        return []