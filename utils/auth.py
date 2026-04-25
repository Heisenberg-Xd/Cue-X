import jwt
from flask import request, jsonify
from functools import wraps
from config import JWT_SECRET_KEY
import logging

logger = logging.getLogger(__name__)

def generate_token(user_id: int) -> str:
    """Generate a JWT token for the given user_id."""
    payload = {
        'user_id': user_id
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token: str) -> int | None:
    """Decode the JWT token and return the user_id, or None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token used.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None

def get_current_user() -> int | None:
    """
    Extract the JWT from the Authorization header and return the user_id.
    Returns None if the token is missing or invalid.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return decode_token(token)

def login_required(f):
    """Decorator to protect routes that require a valid user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_current_user()
        if user_id is None:
            return jsonify({'error': 'Unauthorized. Please log in.'}), 401
        
        # Inject user_id into the view function arguments
        return f(user_id=user_id, *args, **kwargs)
    return decorated_function
