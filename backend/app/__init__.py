import uuid

from flask import Flask, g, jsonify, send_from_directory
from pydantic import ValidationError as PydanticValidationError
from pymysql import MySQLError
from werkzeug.exceptions import HTTPException

from app.config import APP_ENV, MAX_CONTENT_LENGTH, UPLOADS_DIR, validate_production_config
from app.database import get_connection
from app.errors import ApiError
from app.routers.common_router import common_bp
from app.routers.student_router import student_bp
from app.routers.teacher_router import teacher_bp


def create_app(test_config=None) -> Flask:
    validate_production_config()
    app = Flask(__name__)
    app.config.update(
        APP_ENV=APP_ENV,
        MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
    )
    if test_config:
        app.config.update(test_config)

    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(common_bp)

    @app.before_request
    def assign_request_id():
        g.request_id = uuid.uuid4().hex

    @app.after_request
    def add_response_headers(response):
        response.headers["X-Request-ID"] = getattr(g, "request_id", "")
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify(code=error.code, message=error.message), error.status_code

    @app.errorhandler(PydanticValidationError)
    def handle_validation_error(error: PydanticValidationError):
        details = [
            {"field": ".".join(str(part) for part in item["loc"]), "message": item["msg"]}
            for item in error.errors()
        ]
        return jsonify(code=400, message="请求数据无效", errors=details), 400

    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        return jsonify(code=400, message=str(error)), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        status_code = error.code or 500
        return jsonify(code=status_code, message=error.name), status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled request error (request_id=%s)", g.get("request_id", ""))
        return jsonify(
            code=500,
            message="服务器内部错误",
            request_id=getattr(g, "request_id", ""),
        ), 500

    @app.get("/health/live")
    def liveness():
        return jsonify(status="ok")

    @app.get("/health/ready")
    def readiness():
        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
        except MySQLError:
            app.logger.warning("Readiness check failed (request_id=%s)", g.request_id)
            return jsonify(status="unavailable", request_id=g.request_id), 503
        return jsonify(status="ok")

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(UPLOADS_DIR, filename)

    return app
