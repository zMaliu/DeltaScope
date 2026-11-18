from flask import Blueprint, g, request

from app.auth import auth_required
from app.http import validated_json
from app.schemas.math_schemas import GradeSubmitRequest, QuestionCreateRequest
from app.services.grade_service import grade_student_answer
from app.services.question_service import fetch_current_question, publish_weekly_question
from app.services.submission_service import fetch_pending_submissions, fetch_submission_detail

teacher_bp = Blueprint("teacher", __name__, url_prefix="/api/teacher")


@teacher_bp.post("/question/publish")
@auth_required(role="teacher")
def publish_question():
    result = publish_weekly_question(g.user_id, validated_json(QuestionCreateRequest))
    return {"code": 0, "data": result}


@teacher_bp.get("/submissions/pending")
@auth_required(role="teacher")
def pending_submissions():
    question = fetch_current_question()
    if not question:
        return {"code": 0, "data": []}
    data = fetch_pending_submissions(question["id"])
    return {"code": 0, "data": data}


@teacher_bp.post("/submission/grade")
@auth_required(role="teacher")
def grade_submission():
    result = grade_student_answer(validated_json(GradeSubmitRequest))
    return {"code": 0, "data": result}


@teacher_bp.get("/submission/detail")
@auth_required(role="teacher")
def submission_detail():
    submission_id = int(request.args.get("submission_id", "0"))
    if submission_id <= 0:
        raise ValueError("submission_id 无效")
    data = fetch_submission_detail(submission_id)
    return {"code": 0, "data": data}
