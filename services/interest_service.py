from core.db import execute_query, execute_one, execute_statement


def update_interest(
    user_id,
    category
):
    if not user_id or not category:
        return
    try:
        sql_check = "SELECT id, score FROM user_interests WHERE user_id = %s AND category = %s LIMIT 1;"
        existing = execute_one(sql_check, (user_id, category))

        if existing:
            sql_update = "UPDATE user_interests SET score = score + 1, updated_at = NOW() WHERE id = %s;"
            execute_statement(sql_update, (existing["id"],))
        else:
            sql_insert = "INSERT INTO user_interests (user_id, category, score, updated_at) VALUES (%s, %s, 1, NOW());"
            execute_statement(sql_insert, (user_id, category))
    except Exception as e:
        print(f"INTEREST ERROR: {e}")


def get_top_interests(
    user_id
):
    if not user_id:
        return []
    try:
        sql = "SELECT * FROM user_interests WHERE user_id = %s ORDER BY score DESC LIMIT 10;"
        return execute_query(sql, (user_id,))
    except Exception as e:
        print(f"GET INTEREST ERROR: {e}")
        return []