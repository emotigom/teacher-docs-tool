# 교사 기록문구 도우미 MVP 1단계

Hugging Face Spaces에 배포할 Gradio 기반 시제품입니다. 실제 LLM API는 연결하지 않으며, 입력 검증과 규칙 기반 mock 문구 생성, 결과 편집, XLSX 내려받기만 제공합니다.

## 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

테스트는 `pytest -q`로 실행합니다.

## Hugging Face Spaces 설정

1. 새 **Gradio** Space를 만들고 이 저장소의 파일을 업로드합니다.
2. Space Python 버전은 3.10 이상을 선택합니다.
3. `requirements.txt`가 자동 설치됩니다. API 토큰이나 Secret은 이 단계에서 필요하지 않습니다.
4. 기본 실행 파일은 `app.py`입니다. Hugging Face의 Gradio 런타임이 포트와 호스트를 제공합니다.
5. 다운로드 파일은 `/tmp/teacher-record-downloads`에 만들어지고 기본 1시간 뒤 다음 내보내기 시 정리됩니다. 영구 저장소가 아니므로 세션 데이터와 함께 유지되지 않습니다.

## 개인정보와 세션

- 실제 이름 대신 번호 또는 익명 식별값만 입력합니다.
- 전화번호, 이메일, 주민등록번호와 유사한 값은 생성 전 차단합니다. 한글 2~4자 이름처럼 보이는 값은 경고합니다.
- 브라우저 세션별 `gr.State`를 사용하며, 페이지를 닫거나 새로고침하면 작업 데이터가 사라집니다.
- 문구와 개인정보는 애플리케이션 로그로 남기지 않습니다.

## 현재 범위

Mock 문구는 학생별 `주요 활동`, `강점`, `참여 태도`만 조합한 2문장입니다. 관찰하지 않은 사실, 이름, 학교명은 넣지 않습니다. 실제 LLM API 연결은 의도적으로 포함하지 않았습니다.
