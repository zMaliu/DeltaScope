from typing import Literal

from pydantic import BaseModel, Field, root_validator


class RegisterRequest(BaseModel):
    phone: str = ""
    account: str = ""
    password: str = Field(min_length=8, max_length=128)
    role: Literal["student"] = "student"

    @root_validator
    def require_phone_or_account(cls, values):
        if not (values.get("phone") or values.get("account")):
            raise ValueError("请输入手机号")
        return values


class LoginRequest(BaseModel):
    phone: str = ""
    account: str = ""
    password: str = Field(min_length=1, max_length=128)
    role: Literal["", "student", "teacher", "admin"] = ""

    @root_validator
    def require_phone_or_account(cls, values):
        if not (values.get("phone") or values.get("account")):
            raise ValueError("请输入手机号或账号")
        return values


class SelectRoleRequest(BaseModel):
    target_role: Literal["student", "teacher"]
    teacher_auth_code: str = Field(default="", max_length=128)


class WeChatLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=512)


class AccountRequest(BaseModel):
    account: str = Field(min_length=1, max_length=64)


class ProfileUpdateRequest(BaseModel):
    real_name: str = Field(default="", max_length=64)
    college: str = Field(default="", max_length=128)
    nickname: str = Field(default="", max_length=64)
    avatar_url: str = Field(default="", max_length=255)
    major: str = Field(default="", max_length=128)
    school: str = Field(default="", max_length=128)
    grade: str = Field(default="", max_length=32)
    class_name: str = Field(default="", max_length=64)


class ForumPostRequest(BaseModel):
    title: str = Field(min_length=4, max_length=128)
    content: str = Field(min_length=4, max_length=5000)
    channel: Literal["qa", "checkin", "share", "mentor"] = "qa"
    course: str = Field(default="", max_length=64)
