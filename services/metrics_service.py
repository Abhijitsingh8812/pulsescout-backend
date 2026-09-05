from core.db import execute_statement


def increment_view(article_url: str):
    if not article_url:
        return
    try:
        sql = """
            INSERT INTO article_metrics (article_url, views, bookmarks, shares, likes, updated_at)
            VALUES (%s, 1, 0, 0, 0, NOW())
            ON CONFLICT (article_url) DO UPDATE
            SET views = article_metrics.views + 1,
                updated_at = NOW();
        """
        execute_statement(sql, (article_url,))
    except Exception as e:
        print(f"VIEW ERROR: {e}")


def increment_bookmark(article_url: str):
    if not article_url:
        return
    try:
        sql = """
            INSERT INTO article_metrics (article_url, views, bookmarks, shares, likes, updated_at)
            VALUES (%s, 0, 1, 0, 0, NOW())
            ON CONFLICT (article_url) DO UPDATE
            SET bookmarks = article_metrics.bookmarks + 1,
                updated_at = NOW();
        """
        execute_statement(sql, (article_url,))
    except Exception as e:
        print(f"BOOKMARK ERROR: {e}")


def increment_share(article_url: str):
    if not article_url:
        return
    try:
        sql = """
            INSERT INTO article_metrics (article_url, views, bookmarks, shares, likes, updated_at)
            VALUES (%s, 0, 0, 1, 0, NOW())
            ON CONFLICT (article_url) DO UPDATE
            SET shares = article_metrics.shares + 1,
                updated_at = NOW();
        """
        execute_statement(sql, (article_url,))
    except Exception as e:
        print(f"SHARE ERROR: {e}")