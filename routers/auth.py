import re
import hashlib
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import firebase_admin
from firebase_admin import auth as firebase_auth

from services.otp_service import request_otp, verify_otp, init_otp_table
from services.email_service import send_otp_email
from core.security import _firebase_initialized, init_firebase_admin
from core.db import execute_statement

router = APIRouter(prefix="/auth", tags=["Authentication"])

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class EmailOtpRequest(BaseModel):
    email: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp: str


@router.post("/request-email-otp")
def request_email_otp(body: EmailOtpRequest):
    """
    Validates recipient email address, generates a 6-digit OTP,
    and dispatches verification code via email.
    """
    clean_email = body.email.strip().lower()

    if not clean_email or not EMAIL_REGEX.match(clean_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address."
        )

    # Generate OTP & store hash
    success, otp_or_msg, expires_in = request_otp(clean_email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=otp_or_msg
        )

    # Dispatch email
    sent = send_otp_email(clean_email, otp_or_msg)
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to send verification email. Please try again later."
        )

    return {
        "success": True,
        "message": "Verification code sent successfully",
        "expiresIn": expires_in
    }


@router.post("/verify-email-otp")
def verify_email_otp(body: VerifyOtpRequest):
    """
    Verifies 6-digit OTP code, creates/fetches Firebase user identity,
    generates Firebase custom authentication token, and synchronizes user session.
    """
    clean_email = body.email.strip().lower()
    clean_otp = body.otp.strip()

    if not clean_email or not EMAIL_REGEX.match(clean_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address."
        )

    if not clean_otp or len(clean_otp) != 6 or not clean_otp.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The verification code is incorrect."
        )

    # 1. Verify OTP against database
    valid, err_msg = verify_otp(clean_email, clean_otp)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

    # 2. Firebase Admin SDK User Lookup / Creation & Custom Token Generation
    user_uid = None
    custom_token = None
    is_new_user = False
    display_name = None

    try:
        if not _firebase_initialized and len(firebase_admin._apps) == 0:
            init_firebase_admin()

        if len(firebase_admin._apps) > 0:
            try:
                fb_user = firebase_auth.get_user_by_email(clean_email)
                user_uid = fb_user.uid
                display_name = fb_user.display_name
                is_new_user = False
            except firebase_auth.UserNotFoundError:
                fb_user = firebase_auth.create_user(
                    email=clean_email,
                    email_verified=True
                )
                user_uid = fb_user.uid
                is_new_user = True

            token_bytes = firebase_auth.create_custom_token(user_uid)
            custom_token = token_bytes.decode("utf-8") if isinstance(token_bytes, bytes) else str(token_bytes)
    except Exception as e:
        print(f"[AUTH ROUTER WARNING] Firebase Admin SDK operation error: {e}")

    # Fallback if Firebase Admin is uninitialized in local dev
    if not user_uid:
        user_uid = f"user_{hashlib.md5(clean_email.encode()).hexdigest()[:16]}"
        is_new_user = False

    # 3. Synchronize user profile into PostgreSQL database (non-blocking for auth)
    try:
        execute_statement(
            """
            INSERT INTO user_preferences (user_id, preferred_region)
            VALUES (%s, 'global')
            ON CONFLICT (user_id) DO NOTHING;
            """,
            (user_uid,)
        )
    except Exception as e:
        print(f"[AUTH ROUTER WARNING] User DB sync warning: {e}")

    return {
        "success": True,
        "isNewUser": is_new_user,
        "customToken": custom_token,
        "user": {
            "id": user_uid,
            "email": clean_email,
            "name": display_name
        }
    }
