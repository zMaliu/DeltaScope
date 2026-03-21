import os
import uuid

from flask import Blueprint, request
from werkzeug.utils import secure_filename

from app.infra.rank_repository import get_top_users
from app.services.auth_service import login_user, register_user

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
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    os.makedirs(uploads_dir, exist_ok=True)
    filename = secure_filename(file.filename or "image.jpg")
    ext = os.path.splitext(filename)[1] or ".jpg"
    final_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(uploads_dir, final_name)
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
        return {"code": 400, "message": str(exc)}, 400


@common_bp.post("/auth/login")
def login():
    try:
        payload = request.get_json(force=True)
        data = login_user(payload)
        return {"code": 0, "data": data}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400
