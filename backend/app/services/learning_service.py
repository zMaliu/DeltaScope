from typing import Dict, List

from app.infra.learning_repository import (
    create_forum_post,
    get_forum_post,
    get_resource,
    get_learning_event_counts,
    list_forum_posts,
    list_knowledge_nodes,
    list_resources,
    record_learning_event,
)
from app.infra.submission_repository import get_submissions_by_student


def fetch_resource_center(category: str = "") -> Dict:
    resources = list_resources(category=category, limit=30)
    filters = [
        {"label": "全部", "value": ""},
        {"label": "课程资料", "value": "course"},
        {"label": "题目解析", "value": "solution"},
        {"label": "备考专题", "value": "exam"},
    ]
    return {"filters": filters, "resources": resources}


def fetch_resource_detail(resource_id: int) -> Dict:
    resource = get_resource(resource_id)
    if not resource:
        raise ValueError("资源不存在或暂不可查看")
    return resource


def fetch_forum_home(channel: str = "") -> Dict:
    channels = [
        {"name": "提问答疑区", "value": "qa", "desc": "发布课程难题、证明卡点和作业思路。"},
        {"name": "学习打卡区", "value": "checkin", "desc": "记录每日学习进度，形成可见学习轨迹。"},
        {"name": "经验分享区", "value": "share", "desc": "沉淀笔记、复习提纲、真题解析和优秀解法。"},
        {"name": "师生指导区", "value": "mentor", "desc": "教师、助教和高年级同学参与专题指导。"},
    ]
    posts = list_forum_posts(channel=channel, limit=20)
    return {"channels": channels, "posts": posts}


def fetch_forum_post(post_id: int) -> Dict:
    post = get_forum_post(post_id)
    if not post:
        raise ValueError("帖子不存在或已下架")
    return post


def publish_forum_post(user_id: int, payload: Dict) -> Dict:
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    channel = (payload.get("channel") or "qa").strip()
    course = (payload.get("course") or "").strip()
    if channel not in ("qa", "checkin", "share", "mentor"):
        raise ValueError("论坛分区不合法")
    if len(title) < 4:
        raise ValueError("标题至少 4 个字")
    if len(content) < 4:
        raise ValueError("内容至少 4 个字")
    post_id = create_forum_post(
        user_id,
        {
            "title": title[:128],
            "content": content,
            "channel": channel,
            "course": course[:64],
        },
    )
    record_learning_event(user_id, "forum_post", "forum_post", post_id)
    return {"post_id": post_id}


def fetch_knowledge_graph(course: str = "") -> Dict:
    nodes = list_knowledge_nodes(course=course)
    rules = [
        "每个知识点对应一个星球节点。",
        "完成测试或每周一题后点亮节点。",
        "后续由 Veritas 和学情数据推荐下一站。",
    ]
    return {"nodes": nodes, "rules": rules}


def fetch_learning_dashboard(user_id: int) -> Dict:
    counts = get_learning_event_counts(user_id)
    submissions = get_submissions_by_student(user_id)
    submitted_count = len(submissions)
    graded_count = len([item for item in submissions if item.get("status") == "graded"])
    dimensions = [
        {
            "label": "每周一题",
            "value": f"{submitted_count} 次提交",
            "percent": min(100, submitted_count * 25),
        },
        {
            "label": "批改反馈",
            "value": f"{graded_count} 次反馈",
            "percent": min(100, graded_count * 25),
        },
        {
            "label": "论坛活跃",
            "value": f"{counts.get('forum_post', 0)} 次发帖",
            "percent": min(100, counts.get("forum_post", 0) * 20),
        },
        {
            "label": "资源学习",
            "value": f"{counts.get('resource_view', 0)} 次浏览",
            "percent": min(100, counts.get("resource_view", 0) * 15),
        },
    ]
    suggestions: List[str] = [
        "优先保持每周一题连续提交，形成稳定的学习节奏。",
        "批改后及时查看评语，把典型错误沉淀到资源库或论坛讨论。",
        "Veritas 接入前，学情预测先以每周一题、论坛和资源浏览行为为主。",
    ]
    return {"dimensions": dimensions, "suggestions": suggestions}
