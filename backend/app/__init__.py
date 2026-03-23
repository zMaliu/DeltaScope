from flask import Flask, send_from_directory

from app.config import UPLOADS_DIR
from app.routers.common_router import common_bp
from app.routers.student_router import student_bp
from app.routers.teacher_router import teacher_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(common_bp)

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(UPLOADS_DIR, filename)

    return app
