from pydantic import BaseModel
from typing import List, Optional

class CreateSessionRequest(BaseModel):
    student_id_number: int

class CreateSessionResponse(BaseModel):
    session_id: int
    curriculum_id: int

class TranscriptRow(BaseModel):
    course_code: str
    grade: str
    credits_earned: int = 0
    term: str | None = None

class TrackSelectRequest(BaseModel):
    group_id: int

class RecommendationRequest(BaseModel):
    max_credits: Optional[int] = 15
    offered_courses: Optional[List[str]] = None