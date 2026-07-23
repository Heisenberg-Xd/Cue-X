"""
utils/auth.py
-------------
JWT authentication helpers for CUE-X.

login_required decorator:
  - Extracts Bearer token from Authorization header
  - Decodes JWT and returns user_id
  - Verifies user still exists in DB
  - Logs every rejection with exact reason
"""

import logging
import traceback

import jwt
from flask import request, jsonify
from functools import wraps

from config import JWT_SECRET_KEY
from database import get_connection
from sqlalchemy import text

logger = logging.getLogger(__name__)


# ── Token helpers ─────────────────────────────────────────────────────────────

def generate_token(user_id: int) -> str:
    """Generate a JWT token for the given user_id (no expiry — used by legacy callers)."""
    payload = {'user_id': user_id}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')


def decode_token(token: str) -> int | None:
    """
    Decode the JWT token and return the user_id, or None if invalid/expired.
    Logs the exact failure reason every time.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if user_id is None:
            logger.warning("[Auth] decode_token: token valid but 'user_id' claim missing — payload: %s", payload)
            return None
        return int(user_id)
    except jwt.ExpiredSignatureError:
        logger.warning("[Auth] decode_token: token EXPIRED")
        return None
    except jwt.InvalidSignatureError:
        logger.warning(
            "[Auth] decode_token: INVALID SIGNATURE — "
            "JWT_SECRET_KEY on this server may differ from the one that signed the token. "
            "Ensure JWT_SECRET_KEY is set identically in Render env vars."
        )
        return None
    except jwt.DecodeError as e:
        logger.warning("[Auth] decode_token: MALFORMED token — %s", e)
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("[Auth] decode_token: invalid token — %s | type=%s", e, type(e).__name__)
        return None
    except Exception as e:
        logger.error("[Auth] decode_token: unexpected error — %s\n%s", e, traceback.format_exc())
        return None


def get_current_user() -> int | None:
    """
    Extract the JWT from the Authorization header and return the user_id.
    Logs the reason for any failure.
    """
    auth_header = request.headers.get('Authorization', '')

    if not auth_header:
        logger.debug("[Auth] get_current_user: no Authorization header")
        return None

    if not auth_header.startswith('Bearer '):
        logger.warning(
            "[Auth] get_current_user: Authorization header present but does not start with 'Bearer ' — "
            "got: '%s...'", auth_header[:30]
        )
        return None

    token = auth_header.split(' ', 1)[1].strip()
    if not token:
        logger.warning("[Auth] get_current_user: Authorization header has 'Bearer ' but token is empty")
        return None

    return decode_token(token)


# ── Decorator ─────────────────────────────────────────────────────────────────

def login_required(f):
    """
    Protect routes that require a valid authenticated user.

    Injects user_id as the FIRST keyword argument into the decorated function.
    Logs every rejection with the exact reason — never returns a generic message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        endpoint = request.endpoint or f.__name__
        method   = request.method
        path     = request.path

        # ── Step 1: Decode JWT ─────────────────────────────────────────────────
        user_id = get_current_user()
        if user_id is None:
            logger.warning(
                "[Auth] 401 UNAUTHORIZED | endpoint=%s %s %s | reason=JWT missing/invalid/expired",
                method, path, endpoint
            )
            return jsonify({
                'error': 'Unauthorized. Please log in.',
                'detail': 'JWT token is missing, expired, or invalid.'
            }), 401

        # ── Step 2: Verify user still exists in DB ────────────────────────────
        try:
            with get_connection() as conn:
                if conn is None:
                    logger.error(
                        "[Auth] 500 | endpoint=%s %s | user_id=%s | reason=DB engine is None",
                        method, path, user_id
                    )
                    return jsonify({'error': 'Database unavailable. Please try again later.'}), 500

                user = conn.execute(
                    text("SELECT id FROM users WHERE id = :id"),
                    {"id": user_id},
                ).fetchone()

        except Exception as exc:
            logger.error(
                "[Auth] 500 | endpoint=%s %s | user_id=%s | DB error during user lookup\n%s",
                method, path, user_id, traceback.format_exc()
            )
            return jsonify({'error': f'Authentication check failed: {type(exc).__name__}'}), 500

        if not user:
            logger.warning(
                "[Auth] 401 STALE TOKEN | endpoint=%s %s | user_id=%s | "
                "user no longer exists in DB — token is stale",
                method, path, user_id
            )
            return jsonify({
                'error': 'Unauthorized. Please log in again.',
                'detail': f'user_id={user_id} not found in database — account may have been deleted.'
            }), 401

        logger.debug(
            "[Auth] ✅ AUTHENTICATED | endpoint=%s %s | user_id=%s",
            method, path, user_id
        )

        # ── Step 3: Inject user_id and call view ──────────────────────────────
        return f(*args, user_id=user_id, **kwargs)

    return decorated_function


# ── Workspace ownership helper (shared) ───────────────────────────────────────

def verify_workspace_access(conn, workspace_id: int, user_id: int, endpoint: str = "") -> bool:
    """
    Check that workspace_id exists and belongs to user_id.
    Logs detailed info on denial for every call.
    Returns True if access granted, False otherwise.
    """
    try:
        ws = conn.execute(
            text("SELECT id, user_id FROM workspaces WHERE id = :id"),
            {"id": workspace_id}
        ).fetchone()

        if ws is None:
            logger.warning(
                "[Auth] 403 WORKSPACE NOT FOUND | endpoint=%s | "
                "workspace_id=%s | user_id=%s | workspace does not exist",
                endpoint, workspace_id, user_id
            )
            return False

        ws_owner = ws[1]
        if ws_owner != user_id:
            logger.warning(
                "[Auth] 403 OWNERSHIP MISMATCH | endpoint=%s | "
                "workspace_id=%s | requesting user_id=%s | workspace owned by user_id=%s",
                endpoint, workspace_id, user_id, ws_owner
            )
            return False

        return True

    except Exception as exc:
        logger.error(
            "[Auth] verify_workspace_access ERROR | endpoint=%s | workspace_id=%s | user_id=%s\n%s",
            endpoint, workspace_id, user_id, traceback.format_exc()
        )
        return False
