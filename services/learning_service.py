from core.db import execute_one, execute_statement


def learn_topic(
    user_id,
    topic
):
    if not user_id or not topic:
        return
    try:
        sql_check = "SELECT id, score FROM user_topics WHERE user_id = %s AND topic = %s LIMIT 1;"
        rows = execute_one(sql_check, (user_id, topic))

        if rows:
            sql_update = "UPDATE user_topics SET score = score + 1, updated_at = NOW() WHERE id = %s;"
            execute_statement(sql_update, (rows["id"],))
        else:
            sql_insert = "INSERT INTO user_topics (user_id, topic, score, updated_at) VALUES (%s, %s, 1, NOW());"
            execute_statement(sql_insert, (user_id, topic))
    except Exception as e:
        print(f"LEARN TOPIC ERROR: {e}")