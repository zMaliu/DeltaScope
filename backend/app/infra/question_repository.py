import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from app.database import get_connection
from app.models.math_models import QuestionModel


def insert_question(question: QuestionModel) -> int:
    sql = """
    INSERT INTO questions
    (teacher_id, title, content, image_urls, max_score, deadline, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    question.teacher_id,
                    question.title,
                    question.content,
                    json.dumps(question.image_urls, ensure_ascii=False),
                    Decimal(question.max_score),
                    question.deadline,
                    question.status,
                ),
            )
            question_id = cursor.lastrowid
        conn.commit()
    return question_id


def get_current_active_question(now: Optional[datetime] = None) -> Optional[Dict]:
    now = now or datetime.now()
    sql = """
    SELECT id, teacher_id, title, content, image_urls, max_score, deadline, status
    FROM questions
    WHERE status = 'published' AND deadline >= %s
    ORDER BY deadline DESC, id DESC
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (now,))
            result = cursor.fetchone()
    if not result:
        return None
    result["image_urls"] = json.loads(result["image_urls"] or "[]")
    return result
