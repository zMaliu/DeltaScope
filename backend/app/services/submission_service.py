from datetime import datetime
from typing import Dict, List, Optional

from app.infra.question_repository import get_current_active_question
from app.infra.submission_repository import (
    find_submission_by_student,
    get_submission_by_id,
    get_submissions_by_question,
    insert_submission,
)
from app.models.math_models import SubmissionModel
from app.schemas.math_schemas import AnswerSubmitRequest


def submit_answer(student_id: int, payload: dict) -> dict:
    request = AnswerSubmitRequest(**payload)
    current_question = get_current_active_question(datetime.now())
    if not current_question or current_question["id"] != request.question_id:
        raise ValueError("当前题目不可提交")
    if datetime.now() > current_question["deadline"]:
        raise ValueError("已超过截止时间")
    exists = find_submission_by_student(request.question_id, student_id)
    if exists:
        raise ValueError("本周已提交，不能重复提交")
    submission = SubmissionModel(
        id=None,
        question_id=request.question_id,
        student_id=student_id,
        answer_image_urls=request.image_urls,
        submit_time=datetime.now(),
        score=None,
        teacher_comment=None,
        status="submitted",
    )
    submission_id = insert_submission(submission)
    return {"submission_id": submission_id}


def fetch_student_result(question_id: int, student_id: int) -> Optional[Dict]:
    return find_submission_by_student(question_id, student_id)


def fetch_pending_submissions(question_id: int) -> List[Dict]:
    return get_submissions_by_question(question_id, "submitted")


def fetch_submission_detail(submission_id: int) -> Optional[Dict]:
    return get_submission_by_id(submission_id)
