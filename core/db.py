import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

_pool: Optional[ThreadedConnectionPool] = None


def init_db_pool():
    global _pool
    if _pool is not None and not _pool.closed:
        return _pool

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[DATABASE POOL WARNING] DATABASE_URL env var is not set!")
        return None

    try:
        _pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=15,
            dsn=db_url
        )
        print("[DATABASE POOL] Successfully initialized PostgreSQL connection pool.")
        return _pool
    except Exception as e:
        print(f"[DATABASE POOL ERROR] Failed to initialize PostgreSQL pool: {e}")
        return None


def close_db_pool():
    global _pool
    if _pool is not None and not _pool.closed:
        _pool.closeall()
        _pool = None
        print("[DATABASE POOL] Closed PostgreSQL connection pool.")


@contextmanager
def get_db_connection():
    global _pool
    if _pool is None or _pool.closed:
        init_db_pool()

    conn = None
    if _pool is not None and not _pool.closed:
        try:
            conn = _pool.getconn()
            # Test if connection is alive (Neon auto-suspend check)
            if conn.closed != 0:
                _pool.putconn(conn, close=True)
                conn = _pool.getconn()
        except Exception as e:
            print(f"[DATABASE POOL WARNING] Pool checkout error: {e}")
            conn = None

    if conn is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL is not configured.")
        conn = psycopg2.connect(db_url)
        try:
            yield conn
        finally:
            conn.close()
    else:
        try:
            yield conn
        finally:
            try:
                if conn and not conn.closed:
                    _pool.putconn(conn)
            except Exception as e:
                print(f"[DATABASE POOL WARNING] Error releasing connection: {e}")


def execute_query(sql: str, params: Optional[tuple | list | dict] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]


def execute_one(sql: str, params: Optional[tuple | list | dict] = None) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None


def execute_statement(sql: str, params: Optional[tuple | list | dict] = None) -> int:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


def execute_batch(sql: str, param_list: List[tuple | list]) -> int:
    if not param_list:
        return 0
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for params in param_list:
                cur.execute(sql, params)
            conn.commit()
            return len(param_list)
