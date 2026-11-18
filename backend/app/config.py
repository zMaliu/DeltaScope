import os
import secrets
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = str(Path(__file__).resolve().parents[1])
UPLOADS_DIR = os.getenv("UPLOADS_DIR", str(Path(BASE_DIR) / "uploads"))

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
IS_PRODUCTION = APP_ENV == "production"
FLASK_HOST = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_RUN_PORT", "5051"))
FLASK_DEBUG = _env_bool("FLASK_DEBUG", False)
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "deltascope"),
    "charset": "utf8mb4",
    "autocommit": False,
    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
    "read_timeout": int(os.getenv("DB_READ_TIMEOUT", "10")),
    "write_timeout": int(os.getenv("DB_WRITE_TIMEOUT", "10")),
}

ADMIN_CONFIG = {
    "account": os.getenv("ADMIN_ACCOUNT", "admin"),
    "password": os.getenv("ADMIN_PASSWORD", ""),
    "nickname": os.getenv("ADMIN_NICKNAME", "系统管理员"),
}

# The development default follows the user-provided local teacher certification code.
# Production deployments must provide an environment-specific value.
TEACHER_AUTH_CODE = os.getenv("TEACHER_AUTH_CODE", "" if IS_PRODUCTION else "gdutmath")

TOKEN_CONFIG = {
    "secret": os.getenv("TOKEN_SECRET") or secrets.token_urlsafe(32),
    "expires_in": int(os.getenv("TOKEN_EXPIRES_IN", "604800")),
}

WECHAT_CONFIG = {
    "app_id": os.getenv("WECHAT_APP_ID", ""),
    "app_secret": os.getenv("WECHAT_APP_SECRET", ""),
}

ALLOW_HEADER_AUTH = _env_bool("ALLOW_HEADER_AUTH", False)
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
ALLOWED_UPLOAD_EXTENSIONS = {
    item.strip().lower()
    for item in os.getenv("ALLOWED_UPLOAD_EXTENSIONS", ".jpg,.jpeg,.png,.webp").split(",")
    if item.strip()
}


def validate_production_config() -> None:
    if not IS_PRODUCTION:
        return

    required = {
        "DB_PASSWORD": DB_CONFIG["password"],
        "TOKEN_SECRET": os.getenv("TOKEN_SECRET", ""),
        "ADMIN_PASSWORD": ADMIN_CONFIG["password"],
        "TEACHER_AUTH_CODE": TEACHER_AUTH_CODE,
        "WECHAT_APP_ID": WECHAT_CONFIG["app_id"],
        "WECHAT_APP_SECRET": WECHAT_CONFIG["app_secret"],
    }
    missing = sorted(name for name, value in required.items() if not value)
    if missing:
        raise RuntimeError("Missing required production settings: " + ", ".join(missing))
    if len(required["TOKEN_SECRET"]) < 32:
        raise RuntimeError("TOKEN_SECRET must contain at least 32 characters in production")
    if ALLOW_HEADER_AUTH:
        raise RuntimeError("ALLOW_HEADER_AUTH must be disabled in production")
    if FLASK_DEBUG:
        raise RuntimeError("FLASK_DEBUG must be disabled in production")
    if DB_CONFIG["user"].strip().lower() == "root":
        raise RuntimeError("Production must use a dedicated database account, not root")
