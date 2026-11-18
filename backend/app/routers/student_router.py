from flask import Blueprint, g, request

from app.auth import auth_required
from app.http import json_object
from app.services.learning_service import (
    fetch_forum_home,
    fetch_forum_post,
    fetch_knowledge_graph,
    fetch_learning_dashboard,
    fetch_resource_center,
    fetch_resource_detail,
    publish_forum_post,
)
from app.services.question_service import fetch_current_question
from app.services.submission_service import fetch_student_result, submit_answer
from app.schemas.common_schemas import ForumPostRequest
from app.http import validated_json

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.get("/question/current")
@auth_required(role="student")
def current_question():
    question = fetch_current_question()
    return {"code": 0, "data": question}


@student_bp.post("/answer/submit")
@auth_required(role="student")
def submit_student_answer():
    result = submit_answer(g.user_id, json_object())
    return {"code": 0, "data": result}


@student_bp.get("/answer/result")
@auth_required(role="student")
def answer_result():
    question_id = int(request.args.get("question_id", "0"))
    if question_id <= 0:
        raise ValueError("question_id 无效")
    data = fetch_student_result(question_id, g.user_id)
    return {"code": 0, "data": data}


@student_bp.get("/resources")
@auth_required(role="student")
def resource_center():
    category = request.args.get("category", "")
    data = fetch_resource_center(category)
    return {"code": 0, "data": data}


@student_bp.get("/resources/<int:resource_id>")
@auth_required(role="student")
def resource_detail(resource_id: int):
    return {"code": 0, "data": fetch_resource_detail(resource_id)}


@student_bp.get("/forum")
@auth_required(role="student")
def forum_home():
    channel = request.args.get("channel", "")
    data = fetch_forum_home(channel)
    return {"code": 0, "data": data}


@student_bp.get("/forum/post/<int:post_id>")
@auth_required(role="student")
def forum_post_detail(post_id: int):
    return {"code": 0, "data": fetch_forum_post(post_id)}


@student_bp.post("/forum/post")
@auth_required(role="student")
def forum_publish_post():
    data = publish_forum_post(g.user_id, validated_json(ForumPostRequest))
    return {"code": 0, "data": data}


@student_bp.get("/knowledge-graph")
@auth_required(role="student")
def knowledge_graph():
    course = request.args.get("course", "")
    data = fetch_knowledge_graph(course)
    return {"code": 0, "data": data}


@student_bp.get("/learning-dashboard")
@auth_required(role="student")
def learning_dashboard():
    data = fetch_learning_dashboard(g.user_id)
    return {"code": 0, "data": data}
