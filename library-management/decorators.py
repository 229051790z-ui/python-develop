from functools import wraps
from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "")
            if user_role not in roles:
                return {"error": "权限不足"}, 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def get_current_user_id():
    return int(get_jwt_identity())


def get_current_user_role():
    claims = get_jwt()
    return claims.get("role", "")
