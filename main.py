from fastapi import FastAPI
from dotenv import load_dotenv
import threading
from core.security import init_firebase_admin
from core.db import init_db_pool, close_db_pool, execute_one

load_dotenv()

# Initialize Firebase Admin SDK
init_firebase_admin()

from aggregator.merger import aggregate_news

# Auth & OTP
from routers.auth import router as auth_router
from services.otp_service import init_otp_table, cleanup_expired_otps

# Core Routers
from routers.rss import router as rss_router
from routers.article import router as article_router
from routers.db_feed import router as db_feed_router
from routers.metrics import router as metrics_router
from routers.trending import router as trending_router

# Personalization
from routers.user import router as user_router
from routers.recommendations import (
    router as recommendation_router
)
from routers.recommendation_debug import (
    router as recommendation_debug_router
)

# Topics
from routers.topics import (
    router as topics_router
)

# Top News
from routers.top_news import (
    router as top_news_router
)

# Engagement
from routers.engagement import (
    router as engagement_router
)

# Blogs
from routers.blogs import (
    router as blogs_router
)

# World
from routers.world import (
    router as world_router
)

# Discovery
from routers.discovery import (
    router as discovery_router
)

# Bookmarks
from routers.bookmarks import (
    router as bookmark_router
)

# Firebase
from routers.fcm import (
    router as fcm_router
)

# Subscription
from routers.subscriptions import (
    router as subscription_router
)
from routers.payments import (
    router as payments_router
)

# Scheduler
from services.scheduler_service import (
    start_scheduler,
    stop_scheduler
)

app = FastAPI(
    title="PulseScout Backend",
    version="1.8.0"
)


# ==========================================================
# STARTUP & SHUTDOWN
# ==========================================================

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("PULSESCOUT STARTING...")
    print("=" * 60)

    # Initialize Neon PostgreSQL Connection Pool
    init_db_pool()
    init_otp_table()

    try:
        scheduler_thread = threading.Thread(
            target=start_scheduler,
            daemon=True,
            name="PulseScoutScheduler"
        )
        scheduler_thread.start()

        print("=" * 60)
        print("BACKGROUND SCHEDULER INITIALIZED")
        print("=" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"SCHEDULER ERROR: {e}")
        print("=" * 60)

    print("=" * 60)
    print("FASTAPI READY")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    print("=" * 60)
    print("PULSESCOUT SHUTTING DOWN...")
    print("=" * 60)
    try:
        stop_scheduler()
    except Exception as e:
        print(f"Scheduler shutdown error: {e}")
    try:
        close_db_pool()
    except Exception as e:
        print(f"Database pool shutdown error: {e}")
    print("PULSESCOUT SHUTDOWN COMPLETE")


# ==========================================================
# ROUTERS
# ==========================================================

app.include_router(auth_router)
app.include_router(rss_router)
app.include_router(article_router)
app.include_router(db_feed_router)
app.include_router(metrics_router)
app.include_router(trending_router)
app.include_router(user_router)
app.include_router(recommendation_router)
app.include_router(recommendation_debug_router)
app.include_router(topics_router)
app.include_router(top_news_router)
app.include_router(engagement_router)
app.include_router(blogs_router)
app.include_router(world_router)
app.include_router(discovery_router)
app.include_router(bookmark_router)
app.include_router(subscription_router)
app.include_router(payments_router)
app.include_router(fcm_router)


# ==========================================================
# HOME
# ==========================================================

@app.get("/")
def home():
    return {
        "message": "PulseScout Backend Running",
        "version": "1.8.0",
        "status": "online",
        "features": {
            "rss_feeds": True,
            "neon_postgresql": True,
            "scheduler": True,
            "database_feeds": True,
            "metrics": True,
            "trending": True,
            "user_preferences": True,
            "recommendations": True,
            "ranking_engine": True,
            "topic_learning": True,
            "top_news": True,
            "blogs": True,
            "world_news": True,
            "reading_time_tracking": True,
            "likes_tracking": True,
            "shares_tracking": True,
            "freshness_boost": True,
            "trending_boost": True
        }
    }


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
def health():
    db_status = "unknown"
    try:
        res = execute_one("SELECT 1 AS alive;")
        if res and res.get("alive") == 1:
            db_status = "connected"
        else:
            db_status = "error"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "PulseScout Backend",
        "database": db_status
    }


# ==========================================================
# SEARCH
# ==========================================================

@app.get("/search")
def search(query: str):
    articles = aggregate_news(query)
    return {
        "query": query,
        "count": len(articles),
        "articles": articles
    }