import os
from datetime import datetime, timedelta, timezone
import razorpay
from fastapi import HTTPException, status

from core.config_plans import get_plan
from core.db import execute_one, execute_statement

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

_razorpay_client = None


def get_razorpay_client():
    global _razorpay_client
    if _razorpay_client is None:
        key_id = os.getenv("RAZORPAY_KEY_ID", "")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        if not key_id or not key_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Razorpay payment gateway is missing server credentials."
            )
        _razorpay_client = razorpay.Client(auth=(key_id, key_secret))
    return _razorpay_client


def create_order(user_id: str, plan_id: str) -> dict:
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subscription plan: {plan_id}"
        )

    client = get_razorpay_client()

    order_payload = {
        "amount": plan["amount"],
        "currency": plan["currency"],
        "receipt": f"rcpt_{user_id[:8]}_{int(datetime.now(timezone.utc).timestamp())}",
        "notes": {
            "user_id": user_id,
            "plan_id": plan["id"],
            "tier": plan["tier"]
        }
    }

    try:
        razorpay_order = client.order.create(data=order_payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create Razorpay order: {str(e)}"
        )

    order_id = razorpay_order["id"]

    try:
        sql = """
            INSERT INTO subscriptions (user_id, tier, billing_cycle, order_id, amount, currency, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'created')
            ON CONFLICT (user_id) DO UPDATE
            SET order_id = EXCLUDED.order_id,
                tier = EXCLUDED.tier,
                billing_cycle = EXCLUDED.billing_cycle,
                amount = EXCLUDED.amount,
                currency = EXCLUDED.currency,
                status = 'created';
        """
        execute_statement(sql, (
            user_id,
            plan["tier"],
            plan["billing_cycle"],
            order_id,
            plan["amount"],
            plan["currency"]
        ))
    except Exception as e:
        print(f"Warning: Could not insert pending order into PostgreSQL: {e}")

    key_id = os.getenv("RAZORPAY_KEY_ID", "")
    return {
        "order_id": order_id,
        "amount": plan["amount"],
        "currency": plan["currency"],
        "key_id": key_id,
        "plan_id": plan["id"]
    }


def verify_payment(
    user_id: str,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
) -> dict:
    client = get_razorpay_client()

    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature. Verification failed."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signature verification error: {str(e)}"
        )

    # 2. Check Order Ownership & Idempotency from Database
    order_owner_id = None
    try:
        sql_check = "SELECT * FROM subscriptions WHERE order_id = %s LIMIT 1;"
        rec = execute_one(sql_check, (razorpay_order_id,))
        if rec:
            order_owner_id = rec.get("user_id")

            # Enforce Order Ownership Protection:
            # Reject attempt if order belongs to a different user
            if order_owner_id and order_owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: This payment order does not belong to the authenticated user."
                )

            # Idempotency check: verify if order was already activated
            if rec.get("status") == "active":
                return {
                    "success": True,
                    "tier": rec.get("tier", "gold"),
                    "billing_cycle": rec.get("billing_cycle", "monthly"),
                    "payment_id": rec.get("payment_id"),
                    "expires_at": rec.get("expires_at").isoformat() if hasattr(rec.get("expires_at"), "isoformat") else rec.get("expires_at"),
                    "message": "Subscription is already active."
                }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Warning: Idempotency / DB order lookup error: {e}")

    # 3. Fallback / Secondary Ownership Check via Razorpay Order Notes
    if not order_owner_id:
        try:
            rzp_order = client.order.fetch(razorpay_order_id)
            notes = rzp_order.get("notes", {}) if rzp_order else {}
            notes_user_id = notes.get("user_id")
            if notes_user_id and notes_user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: Razorpay order notes user_id mismatch."
                )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Warning: Could not fetch order from Razorpay for notes verification: {e}")

    plan_tier = "gold"
    billing_cycle = "monthly"
    duration_days = 30

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=duration_days)

    try:
        sql_activate = """
            INSERT INTO subscriptions (user_id, tier, billing_cycle, order_id, payment_id, signature, status, starts_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'active', %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET status = 'active',
                tier = EXCLUDED.tier,
                billing_cycle = EXCLUDED.billing_cycle,
                order_id = EXCLUDED.order_id,
                payment_id = EXCLUDED.payment_id,
                signature = EXCLUDED.signature,
                starts_at = EXCLUDED.starts_at,
                expires_at = EXCLUDED.expires_at;
        """
        execute_statement(sql_activate, (
            user_id,
            plan_tier,
            billing_cycle,
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
            now,
            expires_at
        ))
    except Exception as e:
        print(f"Database error during payment verification save: {e}")

    return {
        "success": True,
        "tier": plan_tier,
        "billing_cycle": billing_cycle,
        "payment_id": razorpay_payment_id,
        "expires_at": expires_at.isoformat(),
        "message": "Payment verified and subscription activated successfully."
    }
