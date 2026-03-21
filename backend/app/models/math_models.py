from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass
class QuestionModel:
    id: Optional[int]
    teacher_id: int
    title: str
    content: str
    image_urls: List[str]
    max_score: Decimal
    deadline: datetime
    status: str


@dataclass
class SubmissionModel:
    id: Optional[int]
    question_id: int
    student_id: int
    answer_image_urls: List[str]
    submit_time: datetime
    score: Optional[Decimal]
    teacher_comment: Optional[str]
    status: str
