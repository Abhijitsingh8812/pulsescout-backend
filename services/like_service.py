from core.db import execute_one, execute_statement


def like_article(
    user_id,
    article_url,
    topic
):
    try:
        if user_id and topic:
            sql_check = "SELECT id, score FROM user_topics WHERE user_id = %s AND topic = %s LIMIT 1;"
            rows = execute_one(sql_check, (user_id, topic))
            if rows:
                sql_update = "UPDATE user_topics SET score = score + 20, updated_at = NOW() WHERE id = %s;"
                execute_statement(sql_update, (rows["id"],))
            else:
                sql_insert = "INSERT INTO user_topics (user_id, topic, score, updated_at) VALUES (%s, %s, 20, NOW());"
                execute_statement(sql_insert, (user_id, topic))

        if article_url:
            sql_metric = """
                INSERT INTO article_metrics (article_url, views, bookmarks, shares, likes, updated_at)
                VALUES (%s, 0, 0, 0, 1, NOW())
                ON CONFLICT (article_url) DO UPDATE
                SET likes = article_metrics.likes + 1,
                    updated_at = NOW();
            """
            execute_statement(sql_metric, (article_url,))
    except Exception as e:
        print(f"LIKE ARTICLE ERROR: {e}")