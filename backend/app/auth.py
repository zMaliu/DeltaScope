from functools import wraps
from typing import Optional

from flask import g, request


def auth_required(role: Optional[str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = request.headers.get("X-User-Id")
            user_role = request.headers.get("X-User-Role")
            if not user_id:
                return {"code": 401, "message": "未登录"}, 401
            if role and user_role != role:
                return {"code": 403, "message": "无权限"}, 403
            g.user_id = int(user_id)
            g.user_role = user_role
            return func(*args, **kwargs)

        return wrapper

    return decorator
