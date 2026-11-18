import os
import sys
import unittest
from unittest.mock import MagicMock, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app import create_app
from app.security.token_service import create_token


def auth_headers(user_id=1, role="student"):
    token = create_token({"user_id": user_id, "role": role})
    return {"Authorization": "Bearer " + token}


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
                json={"phone": "13900000002", "password": "devtest123", "role": "student"},
            )
        with patch("app.routers.common_router.login_user", return_value=fake_login):
            login_resp = self.client.post(
                "/api/common/auth/login",
                json={"phone": "13900000002", "password": "devtest123"},
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
                headers=auth_headers(),
            )
        self.assertEqual(with_auth_resp.status_code, 200)
        self.assertEqual(with_auth_resp.json["code"], 0)

        teacher_resp = self.client.get(
            "/api/student/question/current",
            headers=auth_headers(role="teacher"),
        )
        self.assertEqual(teacher_resp.status_code, 403)

    def test_identity_headers_are_not_trusted_by_default(self):
        response = self.client.get(
            "/api/student/question/current",
            headers={"X-User-Id": "1", "X-User-Role": "admin"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["code"], 401)

    def test_student_learning_module_routes(self):
        headers = auth_headers()
        with patch(
            "app.routers.student_router.fetch_resource_center",
            return_value={"filters": [], "resources": []},
        ):
            resources_resp = self.client.get("/api/student/resources", headers=headers)
        with patch(
            "app.routers.student_router.fetch_forum_home",
            return_value={"channels": [], "posts": []},
        ):
            forum_resp = self.client.get("/api/student/forum", headers=headers)
        with patch(
            "app.routers.student_router.fetch_knowledge_graph",
            return_value={"nodes": [], "rules": []},
        ):
            graph_resp = self.client.get("/api/student/knowledge-graph", headers=headers)
        with patch(
            "app.routers.student_router.fetch_learning_dashboard",
            return_value={"dimensions": [], "suggestions": []},
        ):
            dashboard_resp = self.client.get("/api/student/learning-dashboard", headers=headers)

        self.assertEqual(resources_resp.status_code, 200)
        self.assertEqual(forum_resp.status_code, 200)
        self.assertEqual(graph_resp.status_code, 200)
        self.assertEqual(dashboard_resp.status_code, 200)

    def test_forum_post_route_validates_payload(self):
        headers = auth_headers()
        with patch(
            "app.routers.student_router.publish_forum_post",
            return_value={"post_id": 9},
        ) as fake_publish:
            resp = self.client.post(
                "/api/student/forum/post",
                json={"title": "极限定义问题", "content": "这里为什么需要取有限覆盖？", "channel": "qa"},
                headers=headers,
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["data"]["post_id"], 9)
        fake_publish.assert_called_once()

    def test_malformed_json_has_a_stable_client_error(self):
        response = self.client.post(
            "/api/common/auth/login",
            data="{invalid",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["code"], 400)
        self.assertTrue(response.headers.get("X-Request-ID"))

    def test_unexpected_errors_do_not_leak_exception_text(self):
        with patch(
            "app.routers.student_router.fetch_current_question",
            side_effect=RuntimeError("database password leaked"),
        ):
            response = self.client.get(
                "/api/student/question/current",
                headers=auth_headers(),
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json["message"], "服务器内部错误")
        self.assertNotIn("database password leaked", response.get_data(as_text=True))
        self.assertEqual(response.headers["X-Request-ID"], response.json["request_id"])

    def test_liveness_does_not_require_database(self):
        response = self.client.get("/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_readiness_checks_database(self):
        with patch("app.get_connection") as get_connection:
            get_connection.return_value.__enter__.return_value = MagicMock()
            response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_readiness_returns_503_when_database_is_unavailable(self):
        from pymysql import OperationalError

        with patch("app.get_connection", side_effect=OperationalError("connection refused")):
            response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["status"], "unavailable")

    def test_unknown_route_uses_json_error_envelope(self):
        response = self.client.get("/missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["code"], 404)

    def test_registration_validation_runs_before_service(self):
        with patch("app.routers.common_router.register_user") as register_user:
            response = self.client.post(
                "/api/common/auth/register",
                json={"phone": "13900000003", "password": "short"},
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "请求数据无效")
        register_user.assert_not_called()


if __name__ == "__main__":
    unittest.main()
