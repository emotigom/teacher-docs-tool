"""Application-wide configuration."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "교사 기록문구 도우미"
DEFAULT_STUDENT_COUNT = 25
STEP_STUDENT_COUNT = 5
MAX_STUDENT_COUNT = 200
MAX_NOTE_LENGTH = 300
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/tmp/teacher-record-downloads"))
DOWNLOAD_TTL_SECONDS = int(os.getenv("DOWNLOAD_TTL_SECONDS", "3600"))

OBSERVATION_COLUMNS = ["번호", "주요 활동", "강점", "참여 태도", "관찰 메모"]
RESULT_COLUMNS = ["확정", "번호", "최종 문구", "글자 수", "바이트", "유사도", "상태"]
