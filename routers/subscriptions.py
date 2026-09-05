from fastapi import APIRouter, Depends, HTTPException, status
from core.db import execute_one
from core.security import get_current_user

router = APIRouter(
    prefix="/subscription",
    tags=["subscription"]
)


@router.post("/save")
def save_subscription():
    """
    DEPRECATED & DISABLED.
    Subscription activation must go through server-side Razorpay signature verification
    via POST /payments/verify.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="POST /subscription/save is permanently disabled. Subscriptions can only be activated via verified Razorpay payments at POST /payments/verify."
    )


@router.get("/{user_id}")
def get_subscription(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    verified_uid = current_user["uid"]

    if user_id and user_id != verified_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot inspect subscription of another user."
        )

    sql = "SELECT * FROM subscriptions WHERE user_id = %s LIMIT 1;"
    record = execute_one(sql, (verified_uid,))

    if not record:
        return {
            "tier": "free"
        }

    return record