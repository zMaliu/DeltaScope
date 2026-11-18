import os
import uuid

from flask import Blueprint, g, request
from werkzeug.utils import secure_filename

from app.auth import auth_required
from app.config import ALLOWED_UPLOAD_EXTENSIONS, MAX_UPLOAD_MB, UPLOADS_DIR
from app.http import validated_json
from app.infra.rank_repository import get_top_users
from app.services.admin_service import grant_teacher_role, revoke_teacher_role, search_users
from app.services.auth_service import login_user, register_user, select_role, wechat_login
from app.services.profile_service import get_my_profile, update_my_profile
from app.schemas.common_schemas import (
    AccountRequest,
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    SelectRoleRequest,
    WeChatLoginRequest,
)

common_bp = Blueprint("common", __name__, url_prefix="/api/common")


@common_bp.get("/ranking")
def ranking():
    limit = max(1, min(int(request.args.get("limit", "50")), 100))
    data = get_top_users(limit)
    return {"code": 0, "data": data}


@common_bp.post("/upload")
@auth_required()
def upload():
    file = request.files.get("file")
    if not file:
        return {"code": 400, "message": "缺少文件"}, 400
    content_length = request.content_length or 0
    if content_length > MAX_UPLOAD_MB * 1024 * 1024:
        return {"code": 400, "message": f"文件不能超过 {MAX_UPLOAD_MB}MB"}, 400
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    filename = secure_filename(file.filename or "image.jpg")
    ext = os.path.splitext(filename)[1] or ".jpg"
    if ext.lower() not in ALLOWED_UPLOAD_EXTENSIONS:
        return {"code": 400, "message": "仅支持 jpg/jpeg/png/webp 图片"}, 400
    final_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOADS_DIR, final_name)
    file.save(save_path)
    url = f"/uploads/{final_name}"
    return {"code": 0, "url": url}


@common_bp.post("/auth/register")
def register():
    data = register_user(validated_json(RegisterRequest))
    return {"code": 0, "data": data}


@common_bp.post("/auth/login")
def login():
    data = login_user(validated_json(LoginRequest))
    return {"code": 0, "data": data}


@common_bp.post("/auth/wechat-login")
def login_wechat():
    data = wechat_login(validated_json(WeChatLoginRequest))
    return {"code": 0, "data": data}


@common_bp.post("/auth/select-role")
@auth_required()
def auth_select_role():
    payload = validated_json(SelectRoleRequest)
    target_role = payload.get("target_role", "")
    teacher_auth_code = payload.get("teacher_auth_code", "")
    data = select_role(g.user_id, target_role, teacher_auth_code)
    return {"code": 0, "data": data}


@common_bp.get("/admin/users/search")
@auth_required(role="admin")
def admin_search_users():
    keyword = request.args.get("keyword", "")
    data = search_users(keyword)
    return {"code": 0, "data": data}


@common_bp.post("/admin/role/teacher/grant")
@auth_required(role="admin")
def admin_grant_teacher():
    payload = validated_json(AccountRequest)
    data = grant_teacher_role(payload.get("account", ""))
    return {"code": 0, "data": data}


@common_bp.post("/admin/role/teacher/revoke")
@auth_required(role="admin")
def admin_revoke_teacher():
    payload = validated_json(AccountRequest)
    data = revoke_teacher_role(payload.get("account", ""))
    return {"code": 0, "data": data}


@common_bp.get("/profile/me")
@auth_required()
def my_profile():
    phone = g.auth_payload.get("phone", "")
    data = get_my_profile(g.user_id, g.user_role, phone)
    return {"code": 0, "data": data}


@common_bp.post("/profile/update")
@auth_required()
def update_profile():
    data = update_my_profile(g.user_id, g.user_role, validated_json(ProfileUpdateRequest))
    return {"code": 0, "data": data}
