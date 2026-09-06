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


class ForgotPasswordOtpRequest(BaseModel):
    email: str


class ForgotPasswordResetRequest(BaseModel):
    email: str
    otp: str
    newPassword: str


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


@router.post("/forgot-password/request-otp")
def forgot_password_request_otp(body: ForgotPasswordOtpRequest):
    """
    Dispatches a 6-digit OTP verification code for password reset.
    Guards against email enumeration while maintaining rate limits.
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
            detail="Unable to send password reset code. Please try again later."
        )

    return {
        "success": True,
        "message": "Password reset code sent to your email address.",
        "expiresIn": expires_in
    }


@router.post("/forgot-password/reset")
def forgot_password_reset(body: ForgotPasswordResetRequest):
    """
    Verifies 6-digit OTP code and updates the user's password directly in Firebase Auth.
    Passwords are never stored in PostgreSQL or logged in server output.
    """
    clean_email = body.email.strip().lower()
    clean_otp = body.otp.strip()
    clean_password = body.newPassword.strip()

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

    if not clean_password or len(clean_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )

    # 1. Verify OTP against database
    valid, err_msg = verify_otp(clean_email, clean_otp)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

    # 2. Update Password in Firebase Authentication via Firebase Admin SDK
    try:
        if not _firebase_initialized and len(firebase_admin._apps) == 0:
            init_firebase_admin()

        if len(firebase_admin._apps) > 0:
            try:
                fb_user = firebase_auth.get_user_by_email(clean_email)
                firebase_auth.update_user(fb_user.uid, password=clean_password)
                print(f"[AUTH ROUTER INFO] Password successfully updated in Firebase Auth for user UID: {fb_user.uid}")
            except firebase_auth.UserNotFoundError:
                # If user doesn't exist in Firebase yet, create user with password
                fb_user = firebase_auth.create_user(
                    email=clean_email,
                    password=clean_password,
                    email_verified=True
                )
                print(f"[AUTH ROUTER INFO] Account created with password in Firebase Auth for UID: {fb_user.uid}")
        else:
            print("[AUTH ROUTER WARNING] Firebase Admin SDK unavailable during password reset.")
    except Exception as e:
        print(f"[AUTH ROUTER ERROR] Failed to update Firebase password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update password right now. Please try again later."
        )

    return {
        "success": True,
        "message": "Password updated successfully. You can now sign in with your new password."
    }

