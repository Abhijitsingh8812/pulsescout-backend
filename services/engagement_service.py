from core.db import execute_one, execute_statement


def reading_time_score(
    seconds
):
    if seconds >= 60:
        return 10
    if seconds >= 30:
        return 5
    if seconds >= 10:
        return 2
    return 1


def update_reading_time(
    user_id,
    topic,
    seconds
):
    if not user_id or not topic:
        return

    bonus = reading_time_score(seconds)

    try:
        sql_check = "SELECT id, score FROM user_topics WHERE user_id = %s AND topic = %s LIMIT 1;"
        rows = execute_one(sql_check, (user_id, topic))

        if rows:
            sql_update = "UPDATE user_topics SET score = score + %s, updated_at = NOW() WHERE id = %s;"
            execute_statement(sql_update, (bonus, rows["id"]))
        else:
            sql_insert = "INSERT INTO user_topics (user_id, topic, score, updated_at) VALUES (%s, %s, %s, NOW());"
            execute_statement(sql_insert, (user_id, topic, bonus))
    except Exception as e:
        print(f"ENGAGEMENT UPDATE ERROR: {e}")