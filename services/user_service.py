from core.db import execute_one, execute_statement


def save_preferences(
    user_id,
    categories
):
    try:
        sql = """
            INSERT INTO user_preferences (user_id, preferred_categories, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id) DO UPDATE
            SET preferred_categories = EXCLUDED.preferred_categories,
                updated_at = NOW();
        """
        execute_statement(sql, (user_id, categories))
        return True
    except Exception as e:
        print(f"PREFERENCE SAVE ERROR: {e}")
        return False


def get_preferences(user_id):
    try:
        sql = "SELECT * FROM user_preferences WHERE user_id = %s LIMIT 1;"
        return execute_one(sql, (user_id,))
    except Exception as e:
        print(f"PREFERENCE GET ERROR: {e}")
        return None