import hashlib
import hmac
import secrets
from typing import Dict, Optional

from pymysql.err import IntegrityError

from app.config import ADMIN_CONFIG, IS_PRODUCTION, TEACHER_AUTH_CODE, WECHAT_CONFIG
from app.errors import ConflictError
from app.infra.user_repository import (
    create_user,
    create_user_by_openid,
    find_user_by_account,
    find_user_by_id,
    find_user_by_openid,
    update_user_role_by_id,
)
from app.security.token_service import create_token

_PASSWORD_ITERATIONS = 600_000


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = _PASSWORD_ITERATIONS
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    if stored_hash.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt, expect = stored_hash.split("$", 3)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                int(iterations),
            ).hex()
            return hmac.compare_digest(digest, expect)
        except (ValueError, TypeError):
            return False
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored_hash)


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
    raw_phone = payload.get("phone") or payload.get("account") or ""
    password = payload.get("password") or ""
    role = payload.get("role") or "student"
    auth_code = payload.get("auth_code") or ""

    if not isinstance(raw_phone, str) or not isinstance(password, str):
        raise ValueError("手机号和密码格式无效")
    if not isinstance(role, str) or not isinstance(auth_code, str):
        raise ValueError("注册信息格式无效")
    phone = _normalize_phone(raw_phone.strip())
    
    if not phone or len(phone) != 11:
        raise ValueError("请输入11位手机号")
    if len(password) < 8:
        raise ValueError("密码至少需要 8 个字符")
    if role not in ("student", "teacher"):
        raise ValueError("目标角色不合法")
    if role == "teacher":
        if not TEACHER_AUTH_CODE or not hmac.compare_digest(
            auth_code.strip().encode("utf-8"), TEACHER_AUTH_CODE.encode("utf-8")
        ):
            raise ValueError("教研授权码错误")
            
    exists = find_user_by_account(phone)
    if exists:
        raise ConflictError("手机号已注册")
        
    try:
        user_id = create_user(phone, _hash_password(password), "未设置昵称", role)
    except IntegrityError as exc:
        raise ConflictError("手机号已注册") from exc
    return _build_login_result(user_id, phone, "未设置昵称", role)


def login_user(payload: Dict) -> Dict:
    raw_account = payload.get("phone") or payload.get("account") or ""
    password = payload.get("password") or ""
    expected_role = payload.get("role") or ""
    if not isinstance(raw_account, str) or not isinstance(password, str):
        raise ValueError("手机号或密码格式无效")
    if not isinstance(expected_role, str):
        raise ValueError("用户身份无效")
    raw_account = raw_account.strip()
    
    if ADMIN_CONFIG["password"] and raw_account == ADMIN_CONFIG["account"] and hmac.compare_digest(
        password, ADMIN_CONFIG["password"]
    ):
        if expected_role and expected_role != "admin":
            raise ValueError("非管理员账号或选择的身份错误")
        return _build_login_result(0, ADMIN_CONFIG["account"], ADMIN_CONFIG["nickname"], "admin")
        
    account = _normalize_phone(raw_account)
    if not account or not password:
        raise ValueError("手机号和密码不能为空")
        
    user = find_user_by_account(account)
    if not user:
        raise ValueError("手机号或密码错误")
    if not _verify_password(password, user.get("password_hash", "")):
        raise ValueError("手机号或密码错误")
        
    if expected_role and user.get("role") != expected_role:
        raise ValueError("选择的身份与实际不符")
        
    return _build_login_result(user["id"], user["account"], user["nickname"], user["role"], user.get("openid", ""))


def wechat_login(payload: Dict) -> Dict:
    code = payload.get("code") or ""
    if not isinstance(code, str):
        raise ValueError("微信登录凭证无效")
    code = code.strip()
    if not code:
        raise ValueError("缺少微信登录 code")
    openid = _exchange_wechat_code(code) if IS_PRODUCTION else _mock_openid_from_code(code)
    user = find_user_by_openid(openid)
    if not user:
        user_id = create_user_by_openid(openid)
        user = find_user_by_id(user_id)
        if not user:
            raise RuntimeError("新建微信用户后无法读取用户记录")
        user["openid"] = openid
    return _build_login_result(user["id"], user["account"], user["nickname"], user["role"], openid)


def select_role(user_id: int, target_role: str, teacher_auth_code: str = "") -> Dict:
    if not isinstance(target_role, str) or not isinstance(teacher_auth_code, str):
        raise ValueError("身份选择信息无效")
    role = (target_role or "").strip()
    if role not in ("student", "teacher"):
        raise ValueError("目标角色不合法")
    if role == "teacher":
        if not TEACHER_AUTH_CODE or not hmac.compare_digest(
            (teacher_auth_code or "").strip().encode("utf-8"), TEACHER_AUTH_CODE.encode("utf-8")
        ):
            raise ValueError("教研授权码错误")
        update_user_role_by_id(user_id, "teacher")
    if role == "student":
        update_user_role_by_id(user_id, "student")
    user = find_user_by_id(user_id)
    return _build_login_result(user["id"], user["account"], user["nickname"], user["role"], user.get("openid", ""))


def _exchange_wechat_code(code: str) -> str:
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.request import urlopen
    import json

    query = urlencode(
        {
            "appid": WECHAT_CONFIG["app_id"],
            "secret": WECHAT_CONFIG["app_secret"],
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    try:
        with urlopen("https://api.weixin.qq.com/sns/jscode2session?" + query, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError("微信登录服务暂时不可用") from exc
    openid = result.get("openid") if isinstance(result, dict) else None
    if not openid:
        raise ValueError("微信登录凭证无效")
    return openid
