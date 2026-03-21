from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, validator


class QuestionCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    image_urls: List[str] = Field(min_items=1)
    max_score: Decimal = Field(gt=0)
    deadline: datetime

    @validator("image_urls")
    def validate_image_urls(cls, value: List[str]) -> List[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("image_urls 不能为空")
        return cleaned


class AnswerSubmitRequest(BaseModel):
    question_id: int = Field(gt=0)
    image_urls: List[str] = Field(min_items=1)

    @validator("image_urls")
    def validate_answer_urls(cls, value: List[str]) -> List[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("image_urls 不能为空")
        return cleaned


class GradeSubmitRequest(BaseModel):
    submission_id: int = Field(gt=0)
    score: Decimal = Field(ge=0)
    teacher_comment: str = Field(default="")
