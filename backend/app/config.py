import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

FLASK_HOST = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_RUN_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Zykhoainng0527."),
    "database": os.getenv("DB_NAME", "deltascope"),
    "charset": "utf8mb4",
    "autocommit": False,
}

ADMIN_CONFIG = {
    "account": os.getenv("ADMIN_ACCOUNT", "admin"),
    "password": os.getenv("ADMIN_PASSWORD", "admin123456"),
    "nickname": os.getenv("ADMIN_NICKNAME", "系统管理员"),
}

TEACHER_AUTH_CODE = os.getenv("TEACHER_AUTH_CODE", "deltascope2026")

TOKEN_CONFIG = {
    "secret": os.getenv("TOKEN_SECRET", "deltascope-token-secret"),
    "expires_in": int(os.getenv("TOKEN_EXPIRES_IN", "604800")),
}

WECHAT_CONFIG = {
    "app_id": os.getenv("WECHAT_APP_ID", ""),
    "app_secret": os.getenv("WECHAT_APP_SECRET", ""),
}
