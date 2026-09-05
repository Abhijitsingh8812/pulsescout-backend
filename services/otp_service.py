import hashlib
import secrets
import os
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any, Optional, List
from core.db import execute_one, execute_statement, execute_query

# In-Memory Fallback for Local Dev / Testing without DATABASE_URL
_in_memory_store: List[Dict[str, Any]] = []


def _has_db() -> bool:
    return bool(os.getenv("DATABASE_URL"))


def init_otp_table():
    """Ensure the email_otp_codes database table and indexes exist."""
    if not _has_db():
        print("[OTP SERVICE] DATABASE_URL missing. Using in-memory OTP store for dev/testing.")
        return

    sql = """
    CREATE TABLE IF NOT EXISTS email_otp_codes (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        otp_hash VARCHAR(255) NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        attempt_count INT DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        used_at TIMESTAMP WITH TIME ZONE NULL
    );

    CREATE INDEX IF NOT EXISTS idx_email_otp_email ON email_otp_codes(email);
    CREATE INDEX IF NOT EXISTS idx_email_otp_expires_at ON email_otp_codes(expires_at);
    CREATE INDEX IF NOT EXISTS idx_email_otp_created_at ON email_otp_codes(created_at);
    """
    try:
        execute_statement(sql)
        print("[OTP SERVICE] Database table email_otp_codes initialized.")
    except Exception as e:
        print(f"[OTP SERVICE WARNING] Table init error: {e}")


def _hash_otp(email: str, otp: str) -> str:
    """Computes a secure SHA-256 hash of the OTP bound to the normalized email address."""
    salted = f"{otp.strip()}:{email.strip().lower()}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def generate_secure_otp() -> str:
    """Generates a cryptographically secure 6-digit numeric string."""
    return str(secrets.randbelow(900000) + 100000)


def request_otp(email: str) -> Tuple[bool, str, int]:
    """
    Validates rate limits and generates a secure 6-digit OTP.
    Returns (success: bool, message: str, expiresIn: int).
    """
    clean_email = email.strip().lower()
    now = datetime.now(timezone.utc)

    if _has_db():
        try:
            # 1. Enforce 60-second Resend Cooldown
            cooldown_cutoff = now - timedelta(seconds=60)
            recent_req = execute_one(
                """
                SELECT created_at FROM email_otp_codes 
                WHERE email = %s AND created_at > %s AND used_at IS NULL
                ORDER BY created_at DESC LIMIT 1;
                """,
                (clean_email, cooldown_cutoff)
            )
            if recent_req:
                return False, "Please wait 60 seconds before requesting a new code.", 0

            # 2. Enforce 15-minute Rate Limit (Max 3 OTP requests)
            rate_limit_cutoff = now - timedelta(minutes=15)
            recent_count_row = execute_one(
                """
                SELECT COUNT(*) as cnt FROM email_otp_codes
                WHERE email = %s AND created_at > %s;
                """,
                (clean_email, rate_limit_cutoff)
            )
            if recent_count_row and recent_count_row.get("cnt", 0) >= 3:
                return False, "Too many verification attempts. Please try again in 15 minutes.", 0

            # 3. Invalidate previous active OTPs for this email
            execute_statement(
                "UPDATE email_otp_codes SET used_at = %s WHERE email = %s AND used_at IS NULL;",
                (now, clean_email)
            )

            # 4. Generate & Hash OTP
            otp = generate_secure_otp()
            otp_hash = _hash_otp(clean_email, otp)
            expires_at = now + timedelta(minutes=10)

            # 5. Store Hashed OTP in Neon PostgreSQL
            execute_statement(
                """
                INSERT INTO email_otp_codes (email, otp_hash, expires_at, attempt_count, created_at)
                VALUES (%s, %s, %s, 0, %s);
                """,
                (clean_email, otp_hash, expires_at, now)
            )

            return True, otp, 600
        except Exception as e:
            print(f"[OTP SERVICE WARNING] DB OTP request error, falling back to memory: {e}")

    # Fallback In-Memory Implementation
    cooldown_cutoff = now - timedelta(seconds=60)
    for rec in _in_memory_store:
        if rec["email"] == clean_email and rec["created_at"] > cooldown_cutoff and rec["used_at"] is None:
            return False, "Please wait 60 seconds before requesting a new code.", 0

    rate_limit_cutoff = now - timedelta(minutes=15)
    recent_cnt = sum(1 for rec in _in_memory_store if rec["email"] == clean_email and rec["created_at"] > rate_limit_cutoff)
    if recent_cnt >= 3:
        return False, "Too many verification attempts. Please try again in 15 minutes.", 0

    for rec in _in_memory_store:
        if rec["email"] == clean_email and rec["used_at"] is None:
            rec["used_at"] = now

    otp = generate_secure_otp()
    otp_hash = _hash_otp(clean_email, otp)
    expires_at = now + timedelta(minutes=10)

    _in_memory_store.append({
        "id": len(_in_memory_store) + 1,
        "email": clean_email,
        "otp_hash": otp_hash,
        "expires_at": expires_at,
        "attempt_count": 0,
        "created_at": now,
        "used_at": None
    })

    return True, otp, 600


def verify_otp(email: str, otp: str) -> Tuple[bool, str]:
    """
    Verifies the provided 6-digit OTP against stored hash.
    Enforces expiration, single-use, and 5-attempt limit.
    Returns (success: bool, message: str).
    """
    clean_email = email.strip().lower()
    clean_otp = otp.strip()
    now = datetime.now(timezone.utc)

    if _has_db():
        try:
            record = execute_one(
                """
                SELECT id, otp_hash, expires_at, attempt_count 
                FROM email_otp_codes 
                WHERE email = %s AND used_at IS NULL
                ORDER BY created_at DESC LIMIT 1;
                """,
                (clean_email,)
            )

            if not record:
                return False, "Invalid or expired verification code. Please request a new code."

            record_id = record["id"]
            expires_at = record["expires_at"]
            attempt_count = record.get("attempt_count", 0)

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at < now:
                execute_statement("UPDATE email_otp_codes SET used_at = %s WHERE id = %s;", (now, record_id))
                return False, "This verification code has expired. Please request a new code."

            if attempt_count >= 5:
                execute_statement("UPDATE email_otp_codes SET used_at = %s WHERE id = %s;", (now, record_id))
                return False, "Too many incorrect attempts. Please request a new verification code."

            expected_hash = record["otp_hash"]
            computed_hash = _hash_otp(clean_email, clean_otp)

            if not secrets.compare_digest(expected_hash, computed_hash):
                new_attempts = attempt_count + 1
                if new_attempts >= 5:
                    execute_statement(
                        "UPDATE email_otp_codes SET attempt_count = %s, used_at = %s WHERE id = %s;",
                        (new_attempts, now, record_id)
                    )
                    return False, "Too many incorrect attempts. Please request a new verification code."
                else:
                    execute_statement(
                        "UPDATE email_otp_codes SET attempt_count = %s WHERE id = %s;",
                        (new_attempts, record_id)
                    )
                    return False, "The verification code is incorrect."

            execute_statement("UPDATE email_otp_codes SET used_at = %s WHERE id = %s;", (now, record_id))
            return True, "Verification successful"
        except Exception as e:
            print(f"[OTP SERVICE WARNING] DB OTP verify error, falling back to memory: {e}")

    # Fallback In-Memory Verification
    record = None
    for rec in reversed(_in_memory_store):
        if rec["email"] == clean_email and rec["used_at"] is None:
            record = rec
            break

    if not record:
        return False, "Invalid or expired verification code. Please request a new code."

    expires_at = record["expires_at"]
    if expires_at < now:
        record["used_at"] = now
        return False, "This verification code has expired. Please request a new code."

    if record["attempt_count"] >= 5:
        record["used_at"] = now
        return False, "Too many incorrect attempts. Please request a new verification code."

    expected_hash = record["otp_hash"]
    computed_hash = _hash_otp(clean_email, clean_otp)

    if not secrets.compare_digest(expected_hash, computed_hash):
        record["attempt_count"] += 1
        if record["attempt_count"] >= 5:
            record["used_at"] = now
            return False, "Too many incorrect attempts. Please request a new verification code."
        return False, "The verification code is incorrect."

    record["used_at"] = now
    return True, "Verification successful"


def cleanup_expired_otps():
    """Deletes OTP records older than 24 hours to prevent table bloating."""
    if _has_db():
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            deleted = execute_statement("DELETE FROM email_otp_codes WHERE created_at < %s;", (cutoff,))
            print(f"[OTP SERVICE] Cleaned up {deleted} expired OTP records.")
        except Exception as e:
            print(f"[OTP SERVICE WARNING] Cleanup failed: {e}")
