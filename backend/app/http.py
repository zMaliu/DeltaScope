from typing import Type

from flask import request
from pydantic import BaseModel


def json_object() -> dict:
    payload = request.get_json(silent=False)
    if not isinstance(payload, dict):
        raise ValueError("请求内容必须是 JSON 对象")
    return payload


def validated_json(model: Type[BaseModel]) -> dict:
    return model(**json_object()).dict()
