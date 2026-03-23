from functools import wraps
from typing import Optional

from flask import g, request

from app.security.token_service import verify_token


def auth_required(role: Optional[str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            token = ""
            if auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()
            payload = verify_token(token) if token else None
            user_id = payload.get("user_id") if payload else request.headers.get("X-User-Id")
            user_role = payload.get("role") if payload else request.headers.get("X-User-Role")
            if not user_id:
                return {"code": 401, "message": "未登录"}, 401
            if role and user_role != role:
                return {"code": 403, "message": "无权限"}, 403
            g.user_id = int(user_id)
            g.user_role = user_role
            g.auth_payload = payload or {}
            return func(*args, **kwargs)

        return wrapper

    return decorator
