from decimal import Decimal

from app.database import transaction
from app.infra.submission_repository import get_submission_with_question
from app.schemas.math_schemas import GradeSubmitRequest


def grade_student_answer(payload: dict) -> dict:
    request = GradeSubmitRequest(**payload)
    target = get_submission_with_question(request.submission_id)
    if not target:
        raise ValueError("作答记录不存在")
    max_score = Decimal(target["max_score"])
    if request.score > max_score:
        raise ValueError("分数不能超过题目满分")
    with transaction() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE submissions
                SET score = %s, teacher_comment = %s, status = 'graded', graded_at = NOW()
                WHERE id = %s
                """,
                (request.score, request.teacher_comment, request.submission_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("批改更新失败")
            cursor.execute(
                """
                UPDATE users
                SET total_score = COALESCE(total_score, 0) + %s
                WHERE id = %s
                """,
                (request.score, target["student_id"]),
            )
    return {"submission_id": request.submission_id, "score": str(request.score)}
