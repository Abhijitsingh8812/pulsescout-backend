import json
import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# HTTPBearer security scheme (auto_error=False to allow custom error handling & optional auth)
security_scheme = HTTPBearer(auto_error=False)

_firebase_initialized = False


def init_firebase_admin():
    """
    Singleton-safe Firebase Admin SDK initialization.
    Reads credentials from FIREBASE_CREDENTIALS environment variable.
    """
    global _firebase_initialized

    if _firebase_initialized or len(firebase_admin._apps) > 0:
        _firebase_initialized = True
        return

    creds_env = os.getenv("FIREBASE_CREDENTIALS")

    if not creds_env:
        print("[SECURITY WARNING] FIREBASE_CREDENTIALS env var is missing.")
        return

    try:
        if creds_env.strip().startswith("{"):
            cred_dict = json.loads(creds_env)
            if "private_key" in cred_dict and isinstance(cred_dict["private_key"], str):
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_dict)
        elif os.path.exists(creds_env):
            cred = credentials.Certificate(creds_env)
        else:
            print("[SECURITY ERROR] FIREBASE_CREDENTIALS is not valid JSON or file path.")
            return

        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        print("[SECURITY INFO] Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"[SECURITY ERROR] Failed to initialize Firebase Admin SDK: {e}")


def get_current_user(
    auth_header: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> dict:
    """
    Dependency for protected user-specific routes.
    Verifies Firebase ID Token from Authorization: Bearer <token>.
    Raises 401 Unauthorized if token is missing, invalid, or expired.
    Returns decoded token dictionary containing verified 'uid'.
    """
    if not auth_header or not auth_header.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth_header.credentials.strip()

    try:
        # If Firebase Admin hasn't initialized due to missing credentials in dev mode
        if not _firebase_initialized and len(firebase_admin._apps) == 0:
            init_firebase_admin()

        if not _firebase_initialized and len(firebase_admin._apps) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase Admin authentication service unavailable."
            )

        decoded_token = auth.verify_id_token(token)
        return decoded_token

    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_optional_user(
    auth_header: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> dict | None:
    """
    Dependency for public/guest routes that can optionally adapt when a user is authenticated.
    Returns decoded token dict if valid token is provided, or None for guest users.
    Never throws 401 for missing tokens.
    """
    if not auth_header or not auth_header.credentials:
        return None

    token = auth_header.credentials.strip()

    try:
        if not _firebase_initialized and len(firebase_admin._apps) == 0:
            init_firebase_admin()

        if not _firebase_initialized and len(firebase_admin._apps) == 0:
            return None

        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        # Ignore invalid/expired tokens for optional guest access
        return None
