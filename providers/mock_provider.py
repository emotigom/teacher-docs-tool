"""Deterministic, non-LLM provider for the MVP."""
from __future__ import annotations

from providers.base import RecordProvider
from schemas import StudentObservation


class MockProvider(RecordProvider):
    def generate(self, student: StudentObservation) -> str:
        first_parts = [part for part in [student.activity, student.attitude] if part]
        second_parts = [part for part in [student.strength] if part]
        first = "와 관련하여 " + ", ".join(first_parts) + "을 보임." if first_parts else "관찰한 활동에 참여함."
        second = "강점으로 " + ", ".join(second_parts) + "을 기름." if second_parts else "관찰 내용을 바탕으로 참여함."
        return f"{first} {second}"
