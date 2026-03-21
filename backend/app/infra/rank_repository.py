from typing import Dict, List

from app.database import get_connection


def get_top_users(limit: int = 50) -> List[Dict]:
    sql = """
    SELECT
        u.id AS user_id,
        u.nickname,
        u.avatar_url,
        COALESCE(w.week_score, 0) AS week_score,
        u.total_score
    FROM users u
    LEFT JOIN (
        SELECT s.student_id, SUM(s.score) AS week_score, MIN(s.submit_time) AS first_submit_time
        FROM submissions s
        JOIN questions q ON q.id = s.question_id
        WHERE s.status = 'graded'
          AND YEARWEEK(q.deadline, 1) = YEARWEEK(NOW(), 1)
        GROUP BY s.student_id
    ) w ON w.student_id = u.id
    ORDER BY w.week_score DESC, w.first_submit_time ASC, u.id ASC
    LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (limit,))
            return cursor.fetchall()
