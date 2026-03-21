from typing import Dict, Optional

from app.database import get_connection


def find_user_by_account(account: str) -> Optional[Dict]:
    sql = """
    SELECT id, account, password_hash, nickname, avatar_url, role, total_score
    FROM users
    WHERE account = %s
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (account,))
            return cursor.fetchone()


def create_user(account: str, password_hash: str, nickname: str, role: str) -> int:
    sql = """
    INSERT INTO users (openid, account, password_hash, nickname, role, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (account, account, password_hash, nickname, role))
            user_id = cursor.lastrowid
        conn.commit()
    return user_id
