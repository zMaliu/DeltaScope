import os
import uuid

from flask import Blueprint, g, request
from werkzeug.utils import secure_filename

from app.auth import auth_required
from app.config import UPLOADS_DIR
from app.infra.rank_repository import get_top_users
from app.services.admin_service import grant_teacher_role, revoke_teacher_role, search_users
from app.services.auth_service import login_user, register_user, select_role, wechat_login
from app.services.profile_service import get_my_profile, update_my_profile

common_bp = Blueprint("common", __name__, url_prefix="/api/common")


@common_bp.get("/ranking")
def ranking():
    limit = int(request.args.get("limit", "50"))
    data = get_top_users(limit)
    return {"code": 0, "data": data}


@common_bp.post("/upload")
def upload():
    file = request.files.get("file")
    if not file:
        return {"code": 400, "message": "缺少文件"}, 400
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    filename = secure_filename(file.filename or "image.jpg")
    ext = os.path.splitext(filename)[1] or ".jpg"
    final_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOADS_DIR, final_name)
    file.save(save_path)
    url = f"/uploads/{final_name}"
    return {"code": 0, "url": url}


@common_bp.post("/auth/register")
def register():
    try:
        payload = request.get_json(force=True)
        data = register_user(payload)
        return {"code": 0, "data": data}
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return {"code": 400, "message": str(exc)}, 400


@common_bp.post("/auth/login")
def login():
    try:
        payload = request.get_json(force=True)
        data = login_user(payload)
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400


@common_bp.post("/auth/wechat-login")
def login_wechat():
    try:
        payload = request.get_json(force=True)
        data = wechat_login(payload)
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400


@common_bp.post("/auth/select-role")
@auth_required()
def auth_select_role():
    try:
        payload = request.get_json(force=True)
        target_role = payload.get("target_role", "")
        teacher_auth_code = payload.get("teacher_auth_code", "")
        data = select_role(g.user_id, target_role, teacher_auth_code)
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400


@common_bp.get("/admin/users/search")
@auth_required(role="admin")
def admin_search_users():
    keyword = request.args.get("keyword", "")
    data = search_users(keyword)
    return {"code": 0, "data": data}


@common_bp.post("/admin/role/teacher/grant")
@auth_required(role="admin")
def admin_grant_teacher():
    try:
        payload = request.get_json(force=True)
        data = grant_teacher_role(payload.get("account", ""))
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400


@common_bp.post("/admin/role/teacher/revoke")
@auth_required(role="admin")
def admin_revoke_teacher():
    try:
        payload = request.get_json(force=True)
        data = revoke_teacher_role(payload.get("account", ""))
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400


@common_bp.get("/profile/me")
@auth_required()
def my_profile():
    try:
        phone = g.auth_payload.get("phone", "") if hasattr(g, "auth_payload") else ""
        data = get_my_profile(g.user_id, g.user_role, phone)
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400


@common_bp.post("/profile/update")
@auth_required()
def update_profile():
    try:
        payload = request.get_json(force=True)
        data = update_my_profile(g.user_id, g.user_role, payload)
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400
