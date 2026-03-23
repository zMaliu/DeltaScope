import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app import create_app


class FrontBackendFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_register_login_routes(self):
        fake_register = {
            "user_id": 1,
            "account": "demo",
            "nickname": "演示用户",
            "role": "student",
        }
        fake_login = {
            "user_id": 1,
            "account": "demo",
            "nickname": "演示用户",
            "role": "student",
            "headers": {"X-User-Id": "1", "X-User-Role": "student"},
        }
        with patch("app.routers.common_router.register_user", return_value=fake_register):
            register_resp = self.client.post(
                "/api/common/auth/register",
                json={"account": "demo", "password": "123456", "role": "student"},
            )
        with patch("app.routers.common_router.login_user", return_value=fake_login):
            login_resp = self.client.post(
                "/api/common/auth/login",
                json={"account": "demo", "password": "123456"},
            )
        self.assertEqual(register_resp.status_code, 200)
        self.assertEqual(login_resp.status_code, 200)
        self.assertEqual(register_resp.json["code"], 0)
        self.assertEqual(login_resp.json["code"], 0)

    def test_auth_required_for_student_route(self):
        no_auth_resp = self.client.get("/api/student/question/current")
        self.assertEqual(no_auth_resp.status_code, 401)
        with patch(
            "app.routers.student_router.fetch_current_question",
            return_value={"id": 99, "title": "题目", "content": "内容", "image_urls": []},
        ):
            with_auth_resp = self.client.get(
                "/api/student/question/current",
                headers={"X-User-Id": "1", "X-User-Role": "student"},
            )
        self.assertEqual(with_auth_resp.status_code, 200)
        self.assertEqual(with_auth_resp.json["code"], 0)


if __name__ == "__main__":
    unittest.main()
