import json
from decimal import Decimal
from typing import Dict, List, Optional

from app.database import get_connection
from app.models.math_models import SubmissionModel


def insert_submission(submission: SubmissionModel) -> int:
    sql = """
    INSERT INTO submissions
    (question_id, student_id, answer_image_urls, submit_time, score, teacher_comment, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    submission.question_id,
                    submission.student_id,
                    json.dumps(submission.answer_image_urls, ensure_ascii=False),
                    submission.submit_time,
                    submission.score,
                    submission.teacher_comment,
                    submission.status,
                ),
            )
            submission_id = cursor.lastrowid
        conn.commit()
    return submission_id


def find_submission_by_student(question_id: int, student_id: int) -> Optional[Dict]:
    sql = """
    SELECT id, question_id, student_id, answer_image_urls, submit_time, score, teacher_comment, status
    FROM submissions
    WHERE question_id = %s AND student_id = %s
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (question_id, student_id))
            result = cursor.fetchone()
    if not result:
        return None
    result["answer_image_urls"] = json.loads(result["answer_image_urls"] or "[]")
    return result


def get_submissions_by_question(question_id: int, status: Optional[str] = None) -> List[Dict]:
    sql = """
    SELECT id, question_id, student_id, answer_image_urls, submit_time, score, teacher_comment, status
    FROM submissions
    WHERE question_id = %s
    """
    params: list = [question_id]
    if status:
        sql += " AND status = %s"
        params.append(status)
    sql += " ORDER BY submit_time ASC, id ASC"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
    for row in rows:
        row["answer_image_urls"] = json.loads(row["answer_image_urls"] or "[]")
    return rows


def get_submission_with_question(submission_id: int) -> Optional[Dict]:
    sql = """
    SELECT s.id, s.student_id, s.question_id, s.score, s.status, q.max_score
    FROM submissions s
    JOIN questions q ON q.id = s.question_id
    WHERE s.id = %s
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (submission_id,))
            return cursor.fetchone()


def get_submission_by_id(submission_id: int) -> Optional[Dict]:
    sql = """
    SELECT id, question_id, student_id, answer_image_urls, submit_time, score, teacher_comment, status
    FROM submissions
    WHERE id = %s
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (submission_id,))
            row = cursor.fetchone()
    if not row:
        return None
    row["answer_image_urls"] = json.loads(row["answer_image_urls"] or "[]")
    return row


def update_submission_grade(submission_id: int, score: Decimal, teacher_comment: str) -> int:
    sql = """
    UPDATE submissions
    SET score = %s, teacher_comment = %s, status = 'graded', graded_at = NOW()
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (score, teacher_comment, submission_id))
            affected = cursor.rowcount
        conn.commit()
    return affected
