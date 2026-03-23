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


def find_user_by_openid(openid: str) -> Optional[Dict]:
    sql = """
    SELECT id, openid, account, password_hash, nickname, avatar_url, role, total_score
    FROM users
    WHERE openid = %s
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (openid,))
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


def create_user_by_openid(openid: str, nickname: str = "") -> int:
    account = "wx_" + openid[:20]
    name = nickname or ("微信用户" + openid[-6:])
    sql = """
    INSERT INTO users (openid, account, password_hash, nickname, role, created_at, updated_at)
    VALUES (%s, %s, %s, %s, 'student', NOW(), NOW())
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (openid, account, "", name))
            user_id = cursor.lastrowid
        conn.commit()
    return user_id


def find_user_by_id(user_id: int) -> Optional[Dict]:
    sql = """
    SELECT id, openid, account, nickname, avatar_url, role, total_score,
           school, college, major, grade, class_name, real_name
    FROM users
    WHERE id = %s
    LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()


def search_users_by_account(keyword: str, limit: int = 20) -> list:
    sql = """
    SELECT id, account, nickname, avatar_url, role, total_score
    FROM users
    WHERE account LIKE %s
    ORDER BY id DESC
    LIMIT %s
    """
    like_keyword = "%" + keyword + "%"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (like_keyword, limit))
            return cursor.fetchall()


def update_user_role(account: str, role: str) -> int:
    sql = """
    UPDATE users
    SET role = %s, updated_at = NOW()
    WHERE account = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (role, account))
            affected = cursor.rowcount
        conn.commit()
    return affected


def update_user_role_by_id(user_id: int, role: str) -> int:
    sql = """
    UPDATE users
    SET role = %s, updated_at = NOW()
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (role, user_id))
            affected = cursor.rowcount
        conn.commit()
    return affected


def update_user_profile(user_id: int, payload: Dict) -> int:
    sql = """
    UPDATE users
    SET nickname = %s, avatar_url = %s, school = %s, college = %s, major = %s,
        grade = %s, class_name = %s, real_name = %s, updated_at = NOW()
    WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                payload.get("nickname", ""),
                payload.get("avatar_url", ""),
                payload.get("school", ""),
                payload.get("college", ""),
                payload.get("major", ""),
                payload.get("grade", ""),
                payload.get("class_name", ""),
                payload.get("real_name", ""),
                user_id
            ))
            affected = cursor.rowcount
        conn.commit()
    return affected
