from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection
import jwt
import datetime
from config import JWT_SECRET_KEY

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        print("Signup request:", data)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        hashed_password = generate_password_hash(password)

        with get_connection() as conn:
            if conn is None:
                return jsonify({'error': 'Database connection failed'}), 500

            # Using raw cursor to guarantee %s works as expected by user instructions
            cursor = conn.connection.cursor()
            
            # Handle duplicate email
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "User already exists"}), 400

            # Insert into DB
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, hashed_password)
            )
            user_id = cursor.fetchone()[0]
            conn.connection.commit()

        return jsonify({"message": "User created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        print("Login attempt:", email)

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        with get_connection() as conn:
            if conn is None:
                return jsonify({'error': 'Database connection failed'}), 500

            cursor = conn.connection.cursor()
            cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
                
            user_id = user[0]
            stored_password = user[1]

            if not check_password_hash(stored_password, password):
                return jsonify({'error': 'Invalid credentials'}), 401

            token = jwt.encode(
                {
                    "user_id": user_id,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                JWT_SECRET_KEY,
                algorithm="HS256"
            )

            return jsonify({
                "message": "Login successful",
                "token": token
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
