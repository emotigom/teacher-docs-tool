"""Generate review rows using the mock provider only."""
from __future__ import annotations

import pandas as pd

from providers.mock_provider import MockProvider
from schemas import StudentObservation
from services.diversity import similarity_percent
from services.student_table import normalize_student_table


def metrics(text: str) -> tuple[int, int]:
    return len(text), len(text.encode("utf-8"))


def generate_mock_records(value: pd.DataFrame | list | None) -> pd.DataFrame:
    table = normalize_student_table(value)
    provider = MockProvider()
    rows, previous = [], []
    for _, row in table.iterrows():
        student = StudentObservation(student_id=row["번호"], activity=row["주요 활동"], strength=row["강점"], attitude=row["참여 태도"], note=row["관찰 메모"])
        text = provider.generate(student)
        char_count, byte_count = metrics(text)
        similarity = similarity_percent(text, previous)
        rows.append({"확정": True, "번호": row["번호"], "최종 문구": text, "글자 수": char_count, "바이트": byte_count, "유사도": similarity, "상태": "검토 필요" if similarity >= 80 else "생성 완료"})
        previous.append(text)
    return pd.DataFrame(rows)
