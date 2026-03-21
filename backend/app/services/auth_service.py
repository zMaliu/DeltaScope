import hashlib
from typing import Dict

from app.infra.user_repository import create_user, find_user_by_account


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(payload: Dict) -> Dict:
    account = (payload.get("account") or "").strip()
    password = payload.get("password") or ""
    nickname = (payload.get("nickname") or account).strip()
    role = (payload.get("role") or "student").strip()
    if not account or not password:
        raise ValueError("账号和密码不能为空")
    if role not in ("teacher", "student"):
        raise ValueError("角色不合法")
    exists = find_user_by_account(account)
    if exists:
        raise ValueError("账号已存在")
    user_id = create_user(account, _hash_password(password), nickname, role)
    return {
        "user_id": user_id,
        "account": account,
        "nickname": nickname,
        "role": role,
    }


def login_user(payload: Dict) -> Dict:
    account = (payload.get("account") or "").strip()
    password = payload.get("password") or ""
    if not account or not password:
        raise ValueError("账号和密码不能为空")
    user = find_user_by_account(account)
    if not user:
        raise ValueError("账号或密码错误")
    if user.get("password_hash") != _hash_password(password):
        raise ValueError("账号或密码错误")
    return {
        "user_id": user["id"],
        "account": user["account"],
        "nickname": user["nickname"],
        "role": user["role"],
        "headers": {
            "X-User-Id": str(user["id"]),
            "X-User-Role": user["role"],
        },
    }
