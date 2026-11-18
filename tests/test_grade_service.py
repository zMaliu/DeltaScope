import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.services.grade_service import grade_student_answer


class GradeServiceTestCase(unittest.TestCase):
    def _grade_and_read_score_delta(self, previous_score):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = {"score": previous_score}
        transaction = MagicMock()
        transaction.return_value.__enter__.return_value = connection

        with patch(
            "app.services.grade_service.get_submission_with_question",
            return_value={"max_score": Decimal("10"), "student_id": 7},
        ), patch("app.services.grade_service.transaction", transaction):
            grade_student_answer(
                {"submission_id": 9, "score": Decimal("7"), "teacher_comment": ""}
            )

        score_update = cursor.execute.call_args_list[-1]
        return score_update.args[1][0]

    def test_first_grade_adds_the_full_score(self):
        self.assertEqual(self._grade_and_read_score_delta(None), Decimal("7"))

    def test_regrading_applies_only_the_score_difference(self):
        self.assertEqual(self._grade_and_read_score_delta(Decimal("4")), Decimal("3"))


if __name__ == "__main__":
    unittest.main()
