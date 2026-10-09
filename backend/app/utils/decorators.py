from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User


def get_current_user_id():
    """Return the current JWT identity as an integer.
    Flask-JWT-Extended 4.x stores identity as a string; we convert back to int here.
    """
    return int(get_jwt_identity())


def role_required(*allowed_roles):
    """Decorator that checks the authenticated user has one of the allowed roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_current_user_id()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403
            if user.is_blacklisted:
                return jsonify({'error': 'Account is blacklisted'}), 403
            if user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
