import hashlib
from typing import Dict

from app.config import ADMIN_CONFIG, TEACHER_AUTH_CODE
from app.infra.user_repository import (
    create_user,
    create_user_by_openid,
    find_user_by_account,
    find_user_by_id,
    find_user_by_openid,
    update_user_role_by_id,
)
from app.security.token_service import create_token


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _normalize_phone(phone: str) -> str:
    return "".join([ch for ch in phone if ch.isdigit()])


def _mock_openid_from_code(code: str) -> str:
    raw = hashlib.sha256(code.encode("utf-8")).hexdigest()
    return raw[:32]


def _build_login_result(user_id: int, phone: str, nickname: str, role: str, openid: str = "") -> Dict:
    token = create_token(
        {
            "user_id": user_id,
            "role": role,
            "phone": phone,
            "openid": openid,
        }
    )
    return {
        "user_id": user_id,
        "phone": phone,
        "nickname": nickname,
        "role": role,
        "token": token,
    }


def register_user(payload: Dict) -> Dict:
    phone = _normalize_phone((payload.get("phone") or payload.get("account") or "").strip())
    password = payload.get("password") or ""
    role = payload.get("role") or "student"
    auth_code = payload.get("auth_code") or ""
    
    if not phone or len(phone) != 11:
        raise ValueError("请输入11位手机号")
    if not password:
        raise ValueError("手机号和密码不能为空")
    if role not in ("student", "teacher"):
        raise ValueError("目标角色不合法")
    if role == "teacher":
        if auth_code.strip() != TEACHER_AUTH_CODE:
            raise ValueError("教研授权码错误")
            
    exists = find_user_by_account(phone)
    if exists:
        raise ValueError("手机号已注册")
        
    user_id = create_user(phone, _hash_password(password), "未设置昵称", role)
    return _build_login_result(user_id, phone, "未设置昵称", role)


def login_user(payload: Dict) -> Dict:
    raw_account = (payload.get("phone") or payload.get("account") or "").strip()
    password = payload.get("password") or ""
    expected_role = payload.get("role") or ""
    
    if raw_account == ADMIN_CONFIG["account"] and password == ADMIN_CONFIG["password"]:
        if expected_role and expected_role != "admin":
            raise ValueError("非管理员账号或选择的身份错误")
        return _build_login_result(0, ADMIN_CONFIG["account"], ADMIN_CONFIG["nickname"], "admin")
        
    account = _normalize_phone(raw_account)
    if not account or not password:
        raise ValueError("手机号和密码不能为空")
        
    user = find_user_by_account(account)
    if not user:
        raise ValueError("手机号或密码错误")
    if user.get("password_hash") != _hash_password(password):
        raise ValueError("手机号或密码错误")
        
    if expected_role and user.get("role") != expected_role:
        raise ValueError("选择的身份与实际不符")
        
    return _build_login_result(user["id"], user["account"], user["nickname"], user["role"], user.get("openid", ""))


def wechat_login(payload: Dict) -> Dict:
    code = (payload.get("code") or "").strip()
    if not code:
        raise ValueError("缺少微信登录 code")
    openid = _mock_openid_from_code(code)
    user = find_user_by_openid(openid)
    if not user:
        user_id = create_user_by_openid(openid)
        user = find_user_by_id(user_id)
        user["openid"] = openid
    return _build_login_result(user["id"], user["account"], user["nickname"], user["role"], openid)


def select_role(user_id: int, target_role: str, teacher_auth_code: str = "") -> Dict:
    role = (target_role or "").strip()
    if role not in ("student", "teacher"):
        raise ValueError("目标角色不合法")
    if role == "teacher":
        if (teacher_auth_code or "").strip() != TEACHER_AUTH_CODE:
            raise ValueError("教研授权码错误")
        update_user_role_by_id(user_id, "teacher")
    if role == "student":
        update_user_role_by_id(user_id, "student")
    user = find_user_by_id(user_id)
    return _build_login_result(user["id"], user["account"], user["nickname"], user["role"], user.get("openid", ""))
