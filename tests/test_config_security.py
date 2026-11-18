import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app import config


class ProductionConfigTestCase(unittest.TestCase):
    def test_production_requires_secrets(self):
        with patch.object(config, "IS_PRODUCTION", True), patch.dict(
            os.environ, {"TOKEN_SECRET": ""}, clear=False
        ), patch.dict(config.DB_CONFIG, {"password": ""}), patch.dict(
            config.ADMIN_CONFIG, {"password": ""}
        ), patch.object(config, "TEACHER_AUTH_CODE", ""), patch.dict(
            config.WECHAT_CONFIG, {"app_id": "", "app_secret": ""}
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing required production settings"):
                config.validate_production_config()

    def test_production_rejects_identity_header_auth(self):
        required_env = {"TOKEN_SECRET": "configured-test-secret-with-at-least-32-chars"}
        with patch.object(config, "IS_PRODUCTION", True), patch.dict(
            os.environ, required_env, clear=False
        ), patch.dict(config.DB_CONFIG, {"password": "configured-test-db-password"}), patch.dict(
            config.ADMIN_CONFIG, {"password": "configured-test-admin-password"}
        ), patch.object(config, "TEACHER_AUTH_CODE", "configured-test-teacher-code"), patch.dict(
            config.WECHAT_CONFIG,
            {"app_id": "configured-test-app-id", "app_secret": "configured-test-app-secret"},
        ), patch.object(config, "ALLOW_HEADER_AUTH", True):
            with self.assertRaisesRegex(RuntimeError, "ALLOW_HEADER_AUTH"):
                config.validate_production_config()

    def test_production_rejects_short_token_secret(self):
        with patch.object(config, "IS_PRODUCTION", True), patch.dict(
            os.environ, {"TOKEN_SECRET": "too-short"}, clear=False
        ), patch.dict(config.DB_CONFIG, {"password": "configured-test-db-password"}), patch.dict(
            config.ADMIN_CONFIG, {"password": "configured-test-admin-password"}
        ), patch.object(config, "TEACHER_AUTH_CODE", "configured-test-teacher-code"), patch.dict(
            config.WECHAT_CONFIG,
            {"app_id": "configured-test-app-id", "app_secret": "configured-test-app-secret"},
        ), patch.object(config, "ALLOW_HEADER_AUTH", False), patch.object(
            config, "FLASK_DEBUG", False
        ):
            with self.assertRaisesRegex(RuntimeError, "at least 32 characters"):
                config.validate_production_config()

    def test_production_rejects_root_database_account(self):
        with patch.object(config, "IS_PRODUCTION", True), patch.dict(
            os.environ,
            {"TOKEN_SECRET": "configured-test-secret-with-at-least-32-chars"},
            clear=False,
        ), patch.dict(config.DB_CONFIG, {"password": "configured-test-db-password"}), patch.dict(
            config.ADMIN_CONFIG, {"password": "configured-test-admin-password"}
        ), patch.object(config, "TEACHER_AUTH_CODE", "configured-test-teacher-code"), patch.dict(
            config.WECHAT_CONFIG,
            {"app_id": "configured-test-app-id", "app_secret": "configured-test-app-secret"},
        ), patch.object(config, "ALLOW_HEADER_AUTH", False), patch.object(
            config, "FLASK_DEBUG", False
        ):
            with self.assertRaisesRegex(RuntimeError, "dedicated database account"):
                config.validate_production_config()


if __name__ == "__main__":
    unittest.main()
