-- ====================================================================
-- PULSESCOUT PHASE 2.1 — FIX 3 PRODUCTION SQL MIGRATION
-- Database Unique Constraints & Indexing for Neon PostgreSQL
-- ====================================================================

-- --------------------------------------------------------------------
-- STEP 1: AUDIT DUPLICATE RECORDS BEFORE APPLYING CONSTRAINTS
-- Run these queries in PostgreSQL SQL console first to verify zero duplicates:
-- --------------------------------------------------------------------

-- Check duplicate article URLs:
-- SELECT url, COUNT(*) FROM articles GROUP BY url HAVING COUNT(*) > 1;

-- Check duplicate article metrics URLs:
-- SELECT article_url, COUNT(*) FROM article_metrics GROUP BY article_url HAVING COUNT(*) > 1;

-- Check duplicate subscription order IDs:
-- SELECT order_id, COUNT(*) FROM subscriptions WHERE order_id IS NOT NULL GROUP BY order_id HAVING COUNT(*) > 1;

-- Check duplicate user subscriptions:
-- SELECT user_id, COUNT(*) FROM subscriptions WHERE user_id IS NOT NULL GROUP BY user_id HAVING COUNT(*) > 1;


-- --------------------------------------------------------------------
-- STEP 2: APPLY UNIQUE CONSTRAINTS
-- --------------------------------------------------------------------

-- 1. Articles Table Uniqueness (Required for PostgREST on_conflict="url")
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'articles_url_key'
    ) THEN
        ALTER TABLE articles ADD CONSTRAINT articles_url_key UNIQUE (url);
    END IF;
END $$;

-- Performance index for feed queries
CREATE INDEX IF NOT EXISTS idx_articles_region_category_created 
ON articles(region, category, created_at DESC);


-- 2. Article Metrics Uniqueness (Required for on_conflict="article_url")
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'article_metrics_article_url_key'
    ) THEN
        ALTER TABLE article_metrics ADD CONSTRAINT article_metrics_article_url_key UNIQUE (article_url);
    END IF;
END $$;


-- 3. Subscriptions Uniqueness (Required for Order & User Idempotency)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'subscriptions_user_id_key'
    ) THEN
        ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_user_id_key UNIQUE (user_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'subscriptions_order_id_key'
    ) THEN
        ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_order_id_key UNIQUE (order_id);
    END IF;
END $$;


-- 4. FCM Tokens Uniqueness
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fcm_tokens_user_id_key'
    ) THEN
        ALTER TABLE fcm_tokens ADD CONSTRAINT fcm_tokens_user_id_key UNIQUE (user_id);
    END IF;
END $$;


-- 5. Bookmarks Composite Uniqueness
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'bookmarks_user_article_key'
    ) THEN
        ALTER TABLE bookmarks ADD CONSTRAINT bookmarks_user_article_key UNIQUE (user_id, article_url);
    END IF;
END $$;
