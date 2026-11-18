from typing import Dict, List, Optional

from app.database import get_connection


def list_resources(category: str = "", limit: int = 20) -> List[Dict]:
    sql = """
    SELECT id, category, course, title, summary, status, sort_order
    FROM learning_resources
    WHERE status IN ('published', 'planning')
    """
    params: list = []
    if category:
        sql += " AND category = %s"
        params.append(category)
    sql += " ORDER BY sort_order ASC, id ASC LIMIT %s"
    params.append(limit)
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()


def get_resource(resource_id: int) -> Optional[Dict]:
    sql = """
    SELECT id, category, course, title, summary, status
    FROM learning_resources
    WHERE id = %s AND status IN ('published', 'planning')
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (resource_id,))
            return cursor.fetchone()


def list_forum_posts(channel: str = "", limit: int = 20) -> List[Dict]:
    sql = """
    SELECT id, author_id, channel, course, title, content, reply_count, created_at
    FROM forum_posts
    WHERE status = 'published'
    """
    params: list = []
    if channel:
        sql += " AND channel = %s"
        params.append(channel)
    sql += " ORDER BY created_at DESC, id DESC LIMIT %s"
    params.append(limit)
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()


def get_forum_post(post_id: int) -> Optional[Dict]:
    sql = """
    SELECT id, author_id, channel, course, title, content, reply_count, created_at
    FROM forum_posts
    WHERE id = %s AND status = 'published'
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (post_id,))
            return cursor.fetchone()


def create_forum_post(author_id: int, payload: Dict) -> int:
    sql = """
    INSERT INTO forum_posts (author_id, channel, course, title, content, status, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, 'published', NOW(), NOW())
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    author_id,
                    payload.get("channel", "qa"),
                    payload.get("course", ""),
                    payload["title"],
                    payload["content"],
                ),
            )
            post_id = cursor.lastrowid
        conn.commit()
    return post_id


def list_knowledge_nodes(course: str = "") -> List[Dict]:
    sql = """
    SELECT id, parent_id, course, name, description, difficulty, sort_order, status
    FROM knowledge_nodes
    WHERE 1 = 1
    """
    params: list = []
    if course:
        sql += " AND course = %s"
        params.append(course)
    sql += " ORDER BY sort_order ASC, id ASC"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()


def record_learning_event(user_id: int, event_type: str, target_type: str = "", target_id: Optional[int] = None) -> int:
    sql = """
    INSERT INTO learning_events (user_id, event_type, target_type, target_id, created_at)
    VALUES (%s, %s, %s, %s, NOW())
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, event_type, target_type, target_id))
            event_id = cursor.lastrowid
        conn.commit()
    return event_id


def get_learning_event_counts(user_id: int) -> Dict:
    sql = """
    SELECT event_type, COUNT(*) AS count
    FROM learning_events
    WHERE user_id = %s
    GROUP BY event_type
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
    return {row["event_type"]: row["count"] for row in rows}
