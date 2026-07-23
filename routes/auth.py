"""
routes/auth.py
--------------
Authentication endpoints for CUE-X.

Fixed (2026-07): Replaced raw psycopg2 cursor (conn.connection.cursor())
with SQLAlchemy text() queries.  The old approach broke with Neon's
SSL-enforced connections and is incompatible with SQLAlchemy 2.x pooling.
"""

import traceback
import datetime
import logging

import jwt
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_connection
from config import JWT_SECRET_KEY

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ── /api/auth/signup ──────────────────────────────────────────────────────────
@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        logger.info(f"[Auth] Signup request for email: {data.get('email') if data else 'NO BODY'}")

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        email    = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        hashed_password = generate_password_hash(password)

        with get_connection() as conn:
            if conn is None:
                logger.error("[Auth] signup() — database engine is None, cannot register user.")
                return jsonify({'error': 'Database unavailable. Please try again later.'}), 500

            # Check for duplicate email
            existing = conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()

            if existing:
                return jsonify({"error": "An account with this email already exists."}), 400

            # Insert user
            result = conn.execute(
                text(
                    "INSERT INTO users (email, password_hash) "
                    "VALUES (:email, :password_hash) RETURNING id"
                ),
                {"email": email, "password_hash": hashed_password}
            )
            user_id = result.fetchone()[0]

        logger.info(f"[Auth] ✅ User created: id={user_id}, email={email}")
        return jsonify({"message": "User created successfully"}), 201

    except Exception as exc:
        logger.error(
            f"[Auth] signup() UNHANDLED EXCEPTION\n"
            f"  Type : {type(exc).__name__}\n"
            f"  Msg  : {exc}\n"
            f"  Trace:\n{traceback.format_exc()}"
        )
        return jsonify({"error": f"Signup failed: {type(exc).__name__}: {exc}"}), 500


# ── /api/auth/login ───────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        email    = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        logger.info(f"[Auth] Login attempt for: {email}")

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        with get_connection() as conn:
            if conn is None:
                logger.error("[Auth] login() — database engine is None, cannot authenticate.")
                return jsonify({'error': 'Database unavailable. Please try again later.'}), 500

            row = conn.execute(
                text("SELECT id, password_hash FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()

        if not row:
            logger.info(f"[Auth] Login failed — no user found for: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401

        user_id        = row[0]
        stored_hash    = row[1]

        if not check_password_hash(stored_hash, password):
            logger.info(f"[Auth] Login failed — wrong password for: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401

        token = jwt.encode(
            {
                "user_id": user_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            },
            JWT_SECRET_KEY,
            algorithm="HS256",
        )

        logger.info(f"[Auth] ✅ Login successful: user_id={user_id}, email={email}")
        return jsonify({
            "message": "Login successful",
            "token": token,
        }), 200

    except Exception as exc:
        logger.error(
            f"[Auth] login() UNHANDLED EXCEPTION\n"
            f"  Type : {type(exc).__name__}\n"
            f"  Msg  : {exc}\n"
            f"  Trace:\n{traceback.format_exc()}"
        )
        return jsonify({"error": f"Login failed: {type(exc).__name__}: {exc}"}), 500
