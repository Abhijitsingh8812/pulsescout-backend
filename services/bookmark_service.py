from core.db import execute_query, execute_one, execute_statement


def save_bookmark(
    user_id,
    article_url,
    title="",
    description="",
    image_url="",
    source=""
):
    try:
        sql = """
            INSERT INTO user_bookmarks (user_id, article_url, title, description, image_url, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, article_url) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                image_url = EXCLUDED.image_url,
                source = EXCLUDED.source;
        """
        execute_statement(sql, (user_id, article_url, title, description, image_url, source))
        return True
    except Exception as e:
        print(f"BOOKMARK SAVE ERROR: {e}")
        return False


def remove_bookmark(
    user_id,
    article_url
):
    try:
        sql = "DELETE FROM user_bookmarks WHERE user_id = %s AND article_url = %s;"
        execute_statement(sql, (user_id, article_url))
        return True
    except Exception as e:
        print(f"BOOKMARK REMOVE ERROR: {e}")
        return False


def get_user_bookmarks(
    user_id
):
    try:
        sql = "SELECT * FROM user_bookmarks WHERE user_id = %s ORDER BY created_at DESC;"
        return execute_query(sql, (user_id,))
    except Exception as e:
        print(f"BOOKMARK FETCH ERROR: {e}")
        return []


def is_bookmarked(
    user_id,
    article_url
):
    try:
        sql = "SELECT 1 FROM user_bookmarks WHERE user_id = %s AND article_url = %s LIMIT 1;"
        res = execute_one(sql, (user_id, article_url))
        return res is not None
    except Exception as e:
        print(f"BOOKMARK CHECK ERROR: {e}")
        return False