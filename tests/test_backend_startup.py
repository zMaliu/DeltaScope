import os
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

import main


class BackendStartupTestCase(unittest.TestCase):
    def test_existing_ready_backend_is_treated_as_success(self):
        output = StringIO()
        with patch("main._port_is_open", return_value=True), patch(
            "main._existing_backend_state", return_value="ready"
        ), patch.object(main.app, "run") as run_server, redirect_stdout(output):
            main.main()

        run_server.assert_not_called()
        self.assertIn("already running and ready", output.getvalue())

    def test_unready_backend_reports_database_readiness(self):
        with patch("main._port_is_open", return_value=True), patch(
            "main._existing_backend_state", return_value="not_ready"
        ), patch.object(main.app, "run") as run_server:
            with self.assertRaisesRegex(SystemExit, "not ready"):
                main.main()

        run_server.assert_not_called()

    def test_unrelated_process_gets_a_clear_port_conflict(self):
        with patch("main._port_is_open", return_value=True), patch(
            "main._existing_backend_state", return_value="unrecognized"
        ), patch.object(main.app, "run") as run_server:
            with self.assertRaisesRegex(SystemExit, "occupied by another program"):
                main.main()

        run_server.assert_not_called()

    def test_free_port_starts_flask(self):
        with patch("main._port_is_open", return_value=False), patch.object(
            main.app, "run"
        ) as run_server:
            main.main()

        run_server.assert_called_once_with(
            host=main.FLASK_HOST,
            port=main.FLASK_PORT,
            debug=main.FLASK_DEBUG,
        )


if __name__ == "__main__":
    unittest.main()
