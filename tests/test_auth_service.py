import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.services.auth_service import login_user, register_user, select_role
from app.schemas.common_schemas import RegisterRequest


class AuthServiceTestCase(unittest.TestCase):
    def test_registration_schema_defaults_to_student_and_rejects_role_selection(self):
        request = RegisterRequest(phone="13900000008", password="strong-pass-2")
        self.assertEqual(request.role, "student")
        with self.assertRaises(ValueError):
            RegisterRequest(phone="13900000008", password="strong-pass-2", role="teacher")

    def test_registration_rejects_short_password_before_database_access(self):
        with patch("app.services.auth_service.find_user_by_account") as find_user:
            with self.assertRaisesRegex(ValueError, "至少需要 8"):
                register_user({"phone": "13900000004", "password": "short"})
        find_user.assert_not_called()

    def test_teacher_registration_requires_configured_auth_code(self):
        with patch("app.services.auth_service.TEACHER_AUTH_CODE", ""):
            with patch("app.services.auth_service.find_user_by_account") as find_user:
                with self.assertRaisesRegex(ValueError, "授权码错误"):
                    register_user(
                        {
                            "phone": "13900000005",
                            "password": "strong-pass-1",
                            "role": "teacher",
                            "auth_code": "",
                        }
                    )
        find_user.assert_not_called()

    def test_empty_admin_password_never_authenticates(self):
        with patch("app.services.auth_service.ADMIN_CONFIG", {"account": "admin", "password": "", "nickname": "Admin"}):
            with self.assertRaisesRegex(ValueError, "不能为空"):
                login_user({"account": "admin", "password": ""})

    def test_teacher_certification_changes_role_and_returns_replacement_token(self):
        teacher = {
            "id": 7,
            "account": "13900000006",
            "nickname": "同学",
            "role": "teacher",
            "openid": "openid-7",
        }
        with patch("app.services.auth_service.TEACHER_AUTH_CODE", "gdutmath"), patch(
            "app.services.auth_service.update_user_role_by_id", return_value=1
        ) as update_role, patch(
            "app.services.auth_service.find_user_by_id", return_value=teacher
        ):
            result = select_role(7, "teacher", "gdutmath")

        update_role.assert_called_once_with(7, "teacher")
        self.assertEqual(result["role"], "teacher")
        self.assertTrue(result["token"])

    def test_teacher_certification_rejects_an_incorrect_code(self):
        with patch("app.services.auth_service.TEACHER_AUTH_CODE", "gdutmath"), patch(
            "app.services.auth_service.update_user_role_by_id"
        ) as update_role:
            with self.assertRaisesRegex(ValueError, "授权码错误"):
                select_role(7, "teacher", "wrong-code")
        update_role.assert_not_called()

    def test_teacher_certification_rejects_unicode_input_without_server_error(self):
        with patch('app.services.auth_service.TEACHER_AUTH_CODE', 'gdutmath'), patch(
            'app.services.auth_service.update_user_role_by_id'
        ) as update_role:
            with self.assertRaisesRegex(ValueError, '授权码错误'):
                select_role(7, 'teacher', '请输入认证码')
        update_role.assert_not_called()


if __name__ == "__main__":
    unittest.main()
