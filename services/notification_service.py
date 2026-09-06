import firebase_admin
from firebase_admin import messaging
from core.db import execute_query, execute_one, execute_statement
from core.security import init_firebase_admin


def init_sent_notifications_table():
    """
    Idempotently creates the sent_notifications history table.
    Uses UNIQUE(article_url, notification_type) to prevent duplicate notifications.
    """
    try:
        sql = """
            CREATE TABLE IF NOT EXISTS sent_notifications (
                id SERIAL PRIMARY KEY,
                article_url TEXT NOT NULL,
                notification_type VARCHAR(50) NOT NULL DEFAULT 'trending',
                region VARCHAR(20),
                sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                CONSTRAINT sent_notifications_article_type_key UNIQUE(article_url, notification_type)
            );
        """
        execute_statement(sql)
        print("[NOTIFICATION SERVICE] Table sent_notifications verified/created successfully.")
    except Exception as e:
        print(f"[NOTIFICATION SERVICE ERROR] Failed to initialize sent_notifications table: {e}")


def get_unnotified_trending_article():
    """
    Queries the highest-scoring unnotified trending article from recent articles (last 48 hours).
    Score formula: views + (likes * 3) + (shares * 5).
    Excludes articles already present in sent_notifications for notification_type = 'trending'.
    Only candidates with trending_score > 0 are considered.
    """
    try:
        sql = """
            SELECT a.id, a.title, a.summary, a.url, a.image_url, a.source, a.region, a.category, a.published_at,
                   (COALESCE(m.views, 0) + COALESCE(m.likes, 0) * 3 + COALESCE(m.shares, 0) * 5) AS trending_score
            FROM articles a
            JOIN article_metrics m ON a.url = m.article_url
            LEFT JOIN sent_notifications sn ON a.url = sn.article_url AND sn.notification_type = 'trending'
            WHERE sn.article_url IS NULL
              AND a.created_at >= NOW() - INTERVAL '48 HOURS'
              AND (COALESCE(m.views, 0) + COALESCE(m.likes, 0) * 3 + COALESCE(m.shares, 0) * 5) > 0
            ORDER BY trending_score DESC, a.created_at DESC
            LIMIT 1;
        """
        return execute_one(sql)
    except Exception as e:
        print(f"[NOTIFICATION SERVICE ERROR] Query for unnotified trending article failed: {e}")
        return None


def get_active_fcm_tokens() -> list[str]:
    """
    Fetches active FCM device tokens from user_devices table.
    """
    try:
        sql = "SELECT DISTINCT fcm_token FROM user_devices WHERE fcm_token IS NOT NULL AND fcm_token != '';"
        rows = execute_query(sql)
        return [r["fcm_token"] for r in rows if r.get("fcm_token")]
    except Exception as e:
        print(f"[NOTIFICATION SERVICE ERROR] Failed to fetch active FCM tokens: {e}")
        return []


def record_sent_notification(article_url: str, notification_type: str = "trending", region: str = None):
    """
    Records an article URL into sent_notifications to prevent duplicate alerts.
    """
    try:
        sql = """
            INSERT INTO sent_notifications (article_url, notification_type, region, sent_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (article_url, notification_type) DO NOTHING;
        """
        execute_statement(sql, (article_url, notification_type, region))
        print(f"[NOTIFICATION SERVICE] Recorded sent notification for '{article_url}' ({notification_type})")
    except Exception as e:
        print(f"[NOTIFICATION SERVICE ERROR] Failed to record sent notification: {e}")


def send_trending_push_notification(article: dict, tokens: list[str]) -> int:
    """
    Sends a multicast FCM push notification to all active device tokens.
    Payload contains explicit fields:
    - type = "trending"
    - article_url = actual HTTPS web URL
    - article_id = actual HTTPS web URL (for Android reader navigation)
    - db_id = database primary key
    - region = article region
    """
    if not tokens:
        print("[NOTIFICATION SERVICE] No target tokens provided.")
        return 0

    init_firebase_admin()
    if len(firebase_admin._apps) == 0:
        print("[NOTIFICATION SERVICE WARNING] Firebase Admin SDK is not initialized. Skipping FCM send.")
        return 0

    title = f"🔥 Trending: {article.get('title', '')}"
    body = article.get('summary') or article.get('title') or "Check out today's trending story on PulseScout."
    article_url = article.get("url", "")
    db_id = str(article.get("id", ""))
    region = str(article.get("region", "global"))

    data_payload = {
        "type": "trending",
        "article_url": str(article_url),
        "article_id": str(article_url),
        "db_id": db_id,
        "title": str(title),
        "body": str(body),
        "region": region
    }

    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data_payload,
            tokens=tokens
        )
        response = messaging.send_each_for_multicast(message)
        print(f"[FCM PUSH] Multicast sent. Success count: {response.success_count}, Failure count: {response.failure_count}")

        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    print(f"[FCM PUSH WARNING] Token index {idx} failed: {resp.exception}")

        return response.success_count
    except Exception as e:
        print(f"[FCM PUSH ERROR] Exception sending multicast notification: {e}")
        return 0


def check_and_send_trending_notifications():
    """
    Evaluates candidate trending articles and sends FCM push notifications.
    Triggered periodically by scheduler_service.py.
    """
    print("[NOTIFICATION SCHEDULER] Checking for trending topic candidates...")
    init_sent_notifications_table()

    tokens = get_active_fcm_tokens()
    if not tokens:
        print("[NOTIFICATION SCHEDULER] No active FCM device tokens found in database. Skipping job.")
        return

    candidate = get_unnotified_trending_article()
    if not candidate:
        print("[NOTIFICATION SCHEDULER] No candidate trending article found (score > 0 within 48h window). Skipping job.")
        return

    print(f"[TRENDING CANDIDATE FOUND] Title='{candidate.get('title')}', score={candidate.get('trending_score')}, region={candidate.get('region')}")

    success_count = send_trending_push_notification(candidate, tokens)
    if success_count > 0:
        record_sent_notification(
            article_url=candidate["url"],
            notification_type="trending",
            region=candidate.get("region")
        )
    else:
        print("[NOTIFICATION SCHEDULER] Push notification failed or 0 successful deliveries. Article NOT recorded into sent_notifications.")
