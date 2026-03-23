from typing import Dict

from app.infra.user_repository import search_users_by_account, update_user_role


def search_users(keyword: str) -> list:
    text = (keyword or "").strip()
    return search_users_by_account(text, 20)


def grant_teacher_role(account: str) -> Dict:
    value = (account or "").strip()
    if not value:
        raise ValueError("账号不能为空")
    affected = update_user_role(value, "teacher")
    if affected == 0:
        raise ValueError("未找到该账号")
    return {"account": value, "role": "teacher"}


def revoke_teacher_role(account: str) -> Dict:
    value = (account or "").strip()
    if not value:
        raise ValueError("账号不能为空")
    affected = update_user_role(value, "student")
    if affected == 0:
        raise ValueError("未找到该账号")
    return {"account": value, "role": "student"}
