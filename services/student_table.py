"""Canonical student-table operations. Student identifiers are always regenerated."""
from __future__ import annotations

import pandas as pd

from config import DEFAULT_STUDENT_COUNT, MAX_STUDENT_COUNT, OBSERVATION_COLUMNS


def _blank_row(number: int) -> dict[str, str]:
    return {"번호": str(number), "주요 활동": "", "강점": "", "참여 태도": "", "관찰 메모": ""}


def make_student_table(count: int = DEFAULT_STUDENT_COUNT, existing: pd.DataFrame | None = None) -> pd.DataFrame:
    """Build a numbered blank table, retaining non-identifier input where possible."""
    count = max(1, min(int(count), MAX_STUDENT_COUNT))
    rows = [_blank_row(i) for i in range(1, count + 1)]
    table = pd.DataFrame(rows, columns=OBSERVATION_COLUMNS)
    if existing is not None and not existing.empty:
        existing = normalize_student_table(existing)
        for index in range(min(len(existing), count)):
            for column in OBSERVATION_COLUMNS[1:]:
                table.at[index, column] = existing.at[index, column]
    return table


def normalize_student_table(value: pd.DataFrame | list | None) -> pd.DataFrame:
    """Normalize browser data and overwrite the identifier column to protect it."""
    if value is None:
        return make_student_table()
    table = value.copy() if isinstance(value, pd.DataFrame) else pd.DataFrame(value)
    for column in OBSERVATION_COLUMNS:
        if column not in table.columns:
            table[column] = ""
    table = table[OBSERVATION_COLUMNS].fillna("").astype(str)
    table["번호"] = [str(i) for i in range(1, len(table) + 1)]
    return table


def add_students(table: pd.DataFrame, amount: int = 5) -> pd.DataFrame:
    table = normalize_student_table(table)
    return make_student_table(min(len(table) + amount, MAX_STUDENT_COUNT), table)


def remove_students(table: pd.DataFrame, amount: int = 5) -> pd.DataFrame:
    table = normalize_student_table(table)
    return make_student_table(max(1, len(table) - amount), table)
