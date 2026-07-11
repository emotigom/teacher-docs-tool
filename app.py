"""Session-scoped Gradio MVP for teacher record wording assistance."""
from __future__ import annotations

import logging

import gradio as gr
import pandas as pd

from config import DEFAULT_STUDENT_COUNT, MAX_STUDENT_COUNT, OBSERVATION_COLUMNS, RESULT_COLUMNS
from services.exporter import export_xlsx
from services.generator import generate_mock_records
from services.student_table import add_students, make_student_table, normalize_student_table, remove_students
from services.validation import validate_students

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def message(errors: list[str], warnings: list[str]) -> str:
    parts = []
    if errors:
        parts.append("### 입력을 확인해 주세요\n" + "\n".join(f"- {item}" for item in errors))
    if warnings:
        parts.append("### 확인 권장\n" + "\n".join(f"- {item}" for item in warnings))
    return "\n\n".join(parts) if parts else "### 입력 검사가 완료되었습니다\n문구를 생성할 수 있습니다."


def reset_table(count: int, state: dict) -> tuple[pd.DataFrame, dict, str]:
    count = min(MAX_STUDENT_COUNT, max(1, int(count)))
    table = make_student_table(count)
    state = {**state, "students": table, "results": pd.DataFrame(columns=RESULT_COLUMNS)}
    return table, state, f"학생 수를 {count}명으로 설정했습니다."


def change_count(action: str, table: pd.DataFrame, state: dict):
    new_table = add_students(table) if action == "add" else remove_students(table)
    state = {**state, "students": new_table, "results": pd.DataFrame(columns=RESULT_COLUMNS)}
    return new_table, len(new_table), state, f"학생 수: {len(new_table)}명"


def load_example(state: dict):
    sample = pd.read_csv("assets/example_students.csv", dtype=str).fillna("")
    table = make_student_table(DEFAULT_STUDENT_COUNT, sample)
    return table, DEFAULT_STUDENT_COUNT, {**state, "students": table, "results": pd.DataFrame(columns=RESULT_COLUMNS)}, "예시 3명을 불러왔습니다. 나머지 행은 비어 있습니다."


def check_input(table: pd.DataFrame, state: dict):
    table, errors, warnings = validate_students(table)
    return table, {**state, "students": table}, message(errors, warnings)


def generate(table: pd.DataFrame, state: dict):
    table, errors, warnings = validate_students(table)
    if errors:
        return pd.DataFrame(columns=RESULT_COLUMNS), {**state, "students": table}, message(errors, warnings)
    results = generate_mock_records(table)
    return results, {**state, "students": table, "results": results}, message([], warnings)


def update_results(results: pd.DataFrame, state: dict):
    results = results.copy() if isinstance(results, pd.DataFrame) else pd.DataFrame(results, columns=RESULT_COLUMNS)
    if not results.empty:
        for index, text in results["최종 문구"].fillna("").items():
            text = str(text)
            results.at[index, "글자 수"] = len(text)
            results.at[index, "바이트"] = len(text.encode("utf-8"))
    return results, {**state, "results": results}


def download(table: pd.DataFrame, results: pd.DataFrame, state: dict):
    try:
        return export_xlsx(table, results)
    except Exception:  # Never expose internal exception details or personal content.
        logger.exception("Excel export failed")
        raise gr.Error("엑셀 파일을 만들지 못했습니다. 잠시 후 다시 시도해 주세요.")


def build_app() -> gr.Blocks:
    initial = make_student_table()
    with gr.Blocks(
        title="교사 기록문구 도우미",
        analytics_enabled=False,
        css="#students-table table tbody td:first-child { pointer-events: none; background: #f3f4f6; }",
    ) as demo:
        state = gr.State({"students": initial, "results": pd.DataFrame(columns=RESULT_COLUMNS)})
        gr.Markdown("# 교사 기록문구 도우미\n실명·연락처 등 개인정보 없이, 현재 브라우저 세션에서만 작업합니다. 이 MVP는 mock 문구만 생성합니다.")
        with gr.Tab("기본 설정"):
            with gr.Row():
                record_type = gr.Dropdown(["교과 세부능력 및 특기사항", "행동특성 및 종합의견", "자율활동"], value="교과 세부능력 및 특기사항", label="기록 유형")
                tone = gr.Dropdown(["간결한 기록체", "성장 중심 기록체", "객관적 기록체"], value="간결한 기록체", label="문체 유형")
                warmth = gr.Radio(["낮음", "보통", "높음"], value="보통", label="표현 온도")
                praise = gr.Radio(["낮음", "보통", "높음"], value="보통", label="칭찬 밀도")
            with gr.Row():
                emphasis = gr.Dropdown(["참여와 성장", "탐구와 문제 해결", "협업과 소통"], value="참여와 성장", label="강조 요소")
                target = gr.Slider(50, 500, value=150, step=10, label="목표 글자 수")
                subject = gr.Textbox(label="수업명")
                school = gr.Dropdown(["초등학교", "중학교", "고등학교", "기타"], value="초등학교", label="학교급")
            grade = gr.Textbox(label="학년 또는 대상")
            activities = gr.Textbox(label="주요 수업 활동", lines=2)
            common = gr.Textbox(label="공통 수업 설명", lines=3)
            gr.Markdown("기본 설정은 다음 LLM 연동 단계에서 활용할 예정이며, 현재 mock 생성에는 학생 관찰 입력만 사용합니다.")
        with gr.Tab("학생 관찰 입력"):
            gr.Markdown("번호는 서버에서 1부터 다시 부여됩니다. 번호 칸을 바꾸어도 저장·검사·생성 시 자동으로 복원됩니다.")
            count = gr.Number(value=DEFAULT_STUDENT_COUNT, precision=0, minimum=1, maximum=MAX_STUDENT_COUNT, label="학생 수 직접 설정 (1~200)")
            with gr.Row():
                set_count = gr.Button("학생 수 설정")
                add = gr.Button("5명 추가")
                remove = gr.Button("5명 줄이기")
                example = gr.Button("CSV 예시 불러오기")
            students = gr.Dataframe(value=initial, headers=OBSERVATION_COLUMNS, datatype=["str"] * 5, interactive=True, label="학생 관찰 입력", wrap=True, elem_id="students-table")
            validate = gr.Button("입력 검사", variant="secondary")
            input_feedback = gr.Markdown()
        with gr.Tab("결과 검토"):
            gr.Markdown("생성 문구는 직접 수정할 수 있으며 수정 즉시 글자 수와 UTF-8 바이트가 다시 계산됩니다.")
            generate_button = gr.Button("mock 문구 생성", variant="primary")
            results = gr.Dataframe(value=pd.DataFrame(columns=RESULT_COLUMNS), headers=RESULT_COLUMNS, datatype=["bool", "str", "str", "number", "number", "number", "str"], interactive=True, label="결과 검토", wrap=True)
            result_feedback = gr.Markdown()
            download_button = gr.Button("최종 엑셀 다운로드")
            file = gr.File(label="엑셀 파일", visible=True)

        # api_name=False keeps all event endpoints private (not exposed in the API view).
        set_count.click(reset_table, [count, state], [students, state, input_feedback], api_name=False)
        add.click(lambda t, s: change_count("add", t, s), [students, state], [students, count, state, input_feedback], api_name=False)
        remove.click(lambda t, s: change_count("remove", t, s), [students, state], [students, count, state, input_feedback], api_name=False)
        example.click(load_example, [state], [students, count, state, input_feedback], api_name=False)
        validate.click(check_input, [students, state], [students, state, input_feedback], api_name=False)
        generate_button.click(generate, [students, state], [results, state, result_feedback], api_name=False, concurrency_id="llm_generation")
        results.change(update_results, [results, state], [results, state], api_name=False)
        download_button.click(download, [students, results, state], file, api_name=False)
    return demo


demo = build_app().queue(default_concurrency_limit=3)

if __name__ == "__main__":
    demo.launch(show_error=False, show_api=False)
