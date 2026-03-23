import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.database import get_connection


class DatabaseConnectionTestCase(unittest.TestCase):
    def test_can_connect_and_query(self):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 AS ok")
                row = cursor.fetchone()
            self.assertEqual(row["ok"], 1)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
