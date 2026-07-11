"""Pydantic data contracts used by the UI and services."""
from __future__ import annotations

from pydantic import BaseModel, Field


class StudentObservation(BaseModel):
    student_id: str = Field(min_length=1, max_length=30)
    activity: str = ""
    strength: str = ""
    attitude: str = ""
    note: str = Field(default="", max_length=300)


class RecordSettings(BaseModel):
    record_type: str = "교과 세부능력 및 특기사항"
    tone: str = "간결한 기록체"
    warmth: str = "보통"
    praise_density: str = "보통"
    emphasis: str = "참여와 성장"
    target_length: int = 150
    subject: str = ""
    school_level: str = "초등학교"
    grade_or_group: str = ""
    main_activity: str = ""
    common_description: str = ""
