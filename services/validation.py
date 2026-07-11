"""Input validation with privacy-oriented warnings."""
from __future__ import annotations

import re

import pandas as pd

from config import MAX_NOTE_LENGTH
from services.student_table import normalize_student_table

PHONE = re.compile(r"(?<!\d)(?:01[016789]|0[2-6]\d?)[-\s]?\d{3,4}[-\s]?\d{4}(?!\d)")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RRN = re.compile(r"(?<!\d)\d{6}[-\s]?[1-4]\d{6}(?!\d)")
KOREAN_NAME = re.compile(r"(?<![가-힣])[가-힣]{2,4}(?![가-힣])")
PRIVATE_PATTERNS = (("전화번호", PHONE), ("이메일", EMAIL), ("주민등록번호와 유사한 값", RRN))


def validate_students(value: pd.DataFrame | list | None) -> tuple[pd.DataFrame, list[str], list[str]]:
    table = normalize_student_table(value)
    errors: list[str] = []
    warnings: list[str] = []
    if not 1 <= len(table) <= 200:
        errors.append("학생 수는 1명 이상 200명 이하여야 합니다.")
    ids = table["번호"].tolist()
    if len(ids) != len(set(ids)):
        errors.append("학생 번호는 중복될 수 없습니다.")
    observation_columns = ["주요 활동", "강점", "참여 태도", "관찰 메모"]
    signatures = []
    for row_index, row in table.iterrows():
        values = [str(row[column]).strip() for column in observation_columns]
        if not any(values):
            errors.append(f"{row_index + 1}번 학생의 관찰 내용을 한 가지 이상 입력해 주세요.")
        if len(values[-1]) > MAX_NOTE_LENGTH:
            errors.append(f"{row_index + 1}번 학생의 관찰 메모는 300자 이하여야 합니다.")
        signatures.append(tuple(values))
        for text in values:
            for label, pattern in PRIVATE_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{row_index + 1}번 학생 입력에 {label}가 포함되어 있습니다. 삭제해 주세요.")
            if KOREAN_NAME.search(text):
                warnings.append(f"{row_index + 1}번 학생 입력에 실제 이름처럼 보이는 한글 표현이 있습니다. 익명 식별값인지 확인해 주세요.")
    if len(table) > 1 and len(set(signatures)) == 1:
        warnings.append("모든 학생의 관찰 입력이 동일합니다. 학생별 관찰을 확인해 주세요.")
    return table, errors, list(dict.fromkeys(warnings))
