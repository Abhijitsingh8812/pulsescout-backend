import os
import time
import threading
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.rss_service import (
    get_india_category,
    get_global_category
)
from services.discovery_service import (
    get_discovery_news
)
from services.notification_service import (
    check_and_send_trending_notifications
)

# ==========================================================
# SINGLE SCHEDULER INSTANCE & DISTRIBUTED LOCK CONTROL
# ==========================================================

ADVISORY_LOCK_ID = 88492031

scheduler = BackgroundScheduler(
    timezone="UTC"
)

_scheduler_started = False
_scheduler_lock = threading.Lock()
_lock_connection = None


# ==========================================================
# CATEGORY LISTS
# ==========================================================

INDIA_CATEGORIES = [
    "breaking",
    "politics",
    "business",
    "technology",
    "sports",
    "entertainment",
    "auto",
    "health",
    "ai",
    "education",
    "defence",
    "startup",
    "movies",
    "cricket",
    "science"
]

GLOBAL_CATEGORIES = [
    "breaking",
    "politics",
    "business",
    "technology",
    "sports",
    "entertainment",
    "science",
    "health",
    "top stories",
    "us",
    "space",
    "uk",
    "world",
    "crime",
    "climate",
]


# ==========================================================
# PERSISTENT LOCK OWNERSHIP
# ==========================================================

def acquire_session_lock() -> bool:
    """
    Attempts to acquire a persistent PostgreSQL session advisory lock.
    If DATABASE_URL is configured, holds the dedicated TCP connection open.
    Returns True if lock acquired, False if held by another process.
    """
    global _lock_connection
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("[SCHEDULER LOCK] DATABASE_URL not set; running in local process mode.")
        return True

    try:
        import psycopg2
        conn = psycopg2.connect(db_url, connect_timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT pg_try_advisory_lock(%s);", (ADVISORY_LOCK_ID,))
        acquired = cursor.fetchone()[0]

        if acquired:
            _lock_connection = conn
            print("[SCHEDULER LOCK] Leadership lock acquired successfully via PostgreSQL Advisory Lock.")
            return True
        else:
            cursor.close()
            conn.close()
            print("[SCHEDULER LOCK] Lock unavailable (held by another worker process). Skipping scheduler startup.")
            return False

    except Exception as e:
        print(f"[SCHEDULER LOCK ERROR] Connection failed: {e}. Defaulting to single instance startup.")
        return True


def release_session_lock():
    """
    Releases the PostgreSQL advisory lock and closes the persistent connection cleanly.
    """
    global _lock_connection
    if _lock_connection is not None:
        try:
            cursor = _lock_connection.cursor()
            cursor.execute("SELECT pg_advisory_unlock(%s);", (ADVISORY_LOCK_ID,))
            cursor.close()
            _lock_connection.close()
            print("[SCHEDULER LOCK] Released PostgreSQL advisory lock and closed connection.")
        except Exception as e:
            print(f"[SCHEDULER LOCK ERROR] Exception during lock release: {e}")
        finally:
            _lock_connection = None


# ==========================================================
# NEWS UPDATE
# ==========================================================

def update_all_news():
    start_time = time.time()
    print("=" * 70)
    print(f"[SCHEDULER] STARTING PULSESCOUT NEWS UPDATE at {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # INDIA CATEGORIES
    for category in INDIA_CATEGORIES:
        try:
            print(f"[INDIA] Updating {category}")
            get_india_category(category)
        except Exception as e:
            print(f"[INDIA ERROR] {category}: {e}")

    # GLOBAL CATEGORIES
    for category in GLOBAL_CATEGORIES:
        try:
            print(f"[GLOBAL] Updating {category}")
            get_global_category(category)
        except Exception as e:
            print(f"[GLOBAL ERROR] {category}: {e}")

    # DISCOVERY
    try:
        print("[DISCOVERY] Updating")
        get_discovery_news()
    except Exception as e:
        print(f"[DISCOVERY ERROR] {e}")

    elapsed = time.time() - start_time
    print("=" * 70)
    print(f"[SCHEDULER] NEWS UPDATE FINISHED in {elapsed:.2f}s")
    print("=" * 70)


# ==========================================================
# START / STOP SCHEDULER
# ==========================================================

def start_scheduler():
    global _scheduler_started

    with _scheduler_lock:
        if _scheduler_started:
            print("[SCHEDULER] Already running in this process.")
            return

        # Attempt persistent PostgreSQL session lock
        if not acquire_session_lock():
            return

        print("=" * 70)
        print("STARTING PULSESCOUT SCHEDULER (MASTER INSTANCE)")
        print("=" * 70)

        # Run first update 30 seconds after startup
        scheduler.add_job(
            func=update_all_news,
            trigger=DateTrigger(
                run_date=datetime.now(timezone.utc) + timedelta(seconds=30)
            ),
            id="initial_news_update",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )

        # Run recurring update every 15 minutes
        scheduler.add_job(
            func=update_all_news,
            trigger=IntervalTrigger(
                minutes=15
            ),
            id="news_update_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )

        # Run trending notification check every 30 minutes
        scheduler.add_job(
            func=check_and_send_trending_notifications,
            trigger=IntervalTrigger(
                minutes=30
            ),
            id="trending_notification_job",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        print("[SCHEDULER] Trending notification job registered: every 30 minutes")

        scheduler.start()
        _scheduler_started = True

        job = scheduler.get_job("trending_notification_job")
        if job:
            print(
                f"[SCHEDULER] Next trending notification run: {job.next_run_time}"
            )
        else:
            print(
                "[SCHEDULER ERROR] Trending notification job was not found after scheduler startup."
            )

        print("=" * 70)
        print("SCHEDULER STARTED SUCCESSFULLY")
        print("Initial update in 30 seconds")
        print("Recurring update every 15 minutes")
        print("Trending notification check every 30 minutes")
        print("=" * 70)


def stop_scheduler():
    global _scheduler_started
    with _scheduler_lock:
        if not _scheduler_started:
            return
        try:
            scheduler.shutdown(wait=False)
            print("[SCHEDULER] BackgroundScheduler shut down cleanly.")
        except Exception as e:
            print(f"[SCHEDULER ERROR] Shutdown exception: {e}")
        finally:
            release_session_lock()
            _scheduler_started = False