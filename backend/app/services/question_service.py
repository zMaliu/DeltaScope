from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from app.infra.question_repository import get_current_active_question, insert_question
from app.models.math_models import QuestionModel
from app.schemas.math_schemas import QuestionCreateRequest


def publish_weekly_question(teacher_id: int, payload: dict) -> dict:
    request = QuestionCreateRequest(**payload)
    question = QuestionModel(
        id=None,
        teacher_id=teacher_id,
        title=request.title,
        content=request.content,
        image_urls=request.image_urls,
        max_score=Decimal(request.max_score),
        deadline=request.deadline,
        status="published",
    )
    question_id = insert_question(question)
    return {"question_id": question_id}


def fetch_current_question() -> Optional[Dict]:
    current = get_current_active_question(datetime.now())
    return current
