"""XLSX export and bounded cleanup of temporary downloads."""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import DOWNLOAD_DIR, DOWNLOAD_TTL_SECONDS
from services.generator import metrics
from services.student_table import normalize_student_table


def cleanup_downloads(directory: Path = DOWNLOAD_DIR, ttl_seconds: int = DOWNLOAD_TTL_SECONDS) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - ttl_seconds
    for path in directory.glob("교사기록문구_*.xlsx"):
        if path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)


def export_xlsx(students: pd.DataFrame | list | None, results: pd.DataFrame | list | None, directory: Path = DOWNLOAD_DIR) -> str:
    cleanup_downloads(directory)
    students = normalize_student_table(students)
    output = students.copy()
    result_table = results.copy() if isinstance(results, pd.DataFrame) else pd.DataFrame(results or [])
    lookup = result_table.set_index("번호") if not result_table.empty and "번호" in result_table else pd.DataFrame()
    texts = []
    for _, row in output.iterrows():
        text = str(lookup.loc[row["번호"], "최종 문구"]) if not lookup.empty and row["번호"] in lookup.index else ""
        texts.append(text)
    output.insert(0, "사용", True)
    output["글자 수"] = [metrics(text)[0] if text else 0 for text in texts]
    output["바이트"] = [metrics(text)[1] if text else 0 for text in texts]
    output["최종 문구"] = texts
    output["교사 메모"] = ""
    output = output[["사용", "번호", "주요 활동", "강점", "참여 태도", "관찰 메모", "글자 수", "바이트", "최종 문구", "교사 메모"]]
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"교사기록문구_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        output.to_excel(writer, sheet_name="작업용_전체", index=False)
        guide = pd.DataFrame({"안내": ["학생 실명이나 개인정보를 입력하지 마세요.", "최종 문구와 사용 여부를 검토한 뒤 활용하세요."]})
        guide.to_excel(writer, sheet_name="사용안내", index=False)
        workbook = writer.book
        header = workbook.add_format({"bold": True, "bg_color": "#D9EAF7", "border": 1, "text_wrap": True})
        wrap = workbook.add_format({"text_wrap": True, "valign": "top"})
        sheet = writer.sheets["작업용_전체"]
        sheet.freeze_panes(1, 0)
        sheet.autofilter(0, 0, len(output), len(output.columns) - 1)
        sheet.set_row(0, 28, header)
        sheet.set_column("A:A", 8, wrap); sheet.set_column("B:B", 10, wrap)
        sheet.set_column("C:E", 20, wrap); sheet.set_column("F:F", 34, wrap)
        sheet.set_column("G:H", 10, wrap); sheet.set_column("I:I", 55, wrap); sheet.set_column("J:J", 24, wrap)
        writer.sheets["사용안내"].set_column("A:A", 60, wrap)
    return str(path)
