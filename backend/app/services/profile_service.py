from typing import Dict

from app.infra.user_repository import find_user_by_id, update_user_profile


def get_my_profile(user_id: int, role: str, phone: str = "") -> Dict:
    if role == "admin":
        return {
            "user_id": 0,
            "phone": phone,
            "nickname": "系统管理员",
            "avatar_url": "",
            "role": "admin",
            "school": "",
            "college": "",
            "major": "",
            "grade": "",
            "class_name": "",
            "real_name": "",
        }
    user = find_user_by_id(user_id)
    if not user:
        raise ValueError("用户不存在")
    return {
        "user_id": user["id"],
        "phone": user["account"],
        "nickname": user["nickname"],
        "avatar_url": user["avatar_url"],
        "role": user["role"],
        "school": user.get("school", ""),
        "college": user.get("college", ""),
        "major": user.get("major", ""),
        "grade": user.get("grade", ""),
        "class_name": user.get("class_name", ""),
        "real_name": user.get("real_name", ""),
    }


def update_my_profile(user_id: int, role: str, payload: Dict) -> Dict:
    if role == "admin":
        raise ValueError("管理员资料不支持修改")
    
    real_name = (payload.get("real_name") or "").strip()
    college = (payload.get("college") or "").strip()
    
    if not real_name:
        raise ValueError("真实姓名不能为空")
    if not college:
        raise ValueError("学院不能为空")
        
    if role == "teacher":
        # 老师只需姓名和学院，我们可以自动用姓名填充昵称
        payload["nickname"] = real_name
    else:
        # 学生还必须填专业
        major = (payload.get("major") or "").strip()
        if not major:
            raise ValueError("专业不能为空")
        # 如果学生没填昵称，也默认用真实姓名
        nickname = (payload.get("nickname") or "").strip()
        if not nickname:
            payload["nickname"] = real_name
            
    update_user_profile(user_id, payload)
    return get_my_profile(user_id, role)
