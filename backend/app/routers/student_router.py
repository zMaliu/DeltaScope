from flask import Blueprint, g, request

from app.auth import auth_required
from app.services.question_service import fetch_current_question
from app.services.submission_service import fetch_student_result, submit_answer

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.get("/question/current")
@auth_required()
def current_question():
    question = fetch_current_question()
    return {"code": 0, "data": question}


@student_bp.post("/answer/submit")
@auth_required()
def submit_student_answer():
    try:
        result = submit_answer(g.user_id, request.get_json(force=True))
        return {"code": 0, "data": result}
    except Exception as exc:
        return {"code": 400, "message": str(exc)}, 400


@student_bp.get("/answer/result")
@auth_required()
def answer_result():
    question_id = int(request.args.get("question_id", "0"))
    if question_id <= 0:
        return {"code": 400, "message": "question_id 无效"}, 400
    data = fetch_student_result(question_id, g.user_id)
    return {"code": 0, "data": data}
