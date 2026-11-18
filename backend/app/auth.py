from functools import wraps
from typing import Optional

from flask import g, request

from app.config import ALLOW_HEADER_AUTH
from app.errors import AuthenticationError, AuthorizationError
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
            header_user_id = request.headers.get("X-User-Id") if ALLOW_HEADER_AUTH else None
            header_user_role = request.headers.get("X-User-Role") if ALLOW_HEADER_AUTH else None
            user_id = payload.get("user_id") if payload else header_user_id
            user_role = payload.get("role") if payload else header_user_role
            if user_id is None or user_id == "":
                raise AuthenticationError()
            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                raise AuthenticationError()
            if user_id < 0 or user_role not in {"student", "teacher", "admin"}:
                raise AuthenticationError()
            if role and user_role != role:
                raise AuthorizationError()
            g.user_id = user_id
            g.user_role = user_role
            g.auth_payload = payload or {}
            return func(*args, **kwargs)

        return wrapper

    return decorator
