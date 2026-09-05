from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.db import execute_statement
from core.security import get_current_user

router = APIRouter(
    prefix="/fcm",
    tags=["FCM"]
)

class FcmTokenRequest(BaseModel):
    user_id: Optional[str] = None
    fcm_token: str
    device_name: str = "Android"
    platform: str = "android"


@router.post("/register")
def register_fcm_token(
    payload: FcmTokenRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    try:
        sql = """
            INSERT INTO user_devices (user_id, fcm_token, device_name, platform, updated_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (user_id) DO UPDATE
            SET fcm_token = EXCLUDED.fcm_token,
                device_name = EXCLUDED.device_name,
                platform = EXCLUDED.platform,
                updated_at = NOW();
        """
        execute_statement(sql, (user_id, payload.fcm_token, payload.device_name, payload.platform))

        return {
            "success": True,
            "message": "FCM token saved"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }