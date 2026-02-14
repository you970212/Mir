# Mir - 개인 로컬 AI 챗봇 (Claude 스타일)

`Mir`는 **내 PC에서만 동작하는 개인 AI 챗봇**입니다.  
`local_claude.py`를 실행하면 터미널에서 `Mira`와 대화할 수 있고, AI 추론은 **Ollama**가 담당합니다.

---

## 무엇을 할 수 있나요?

- 인터넷 없이(로컬 환경에서) AI 대화
- 대화 기록 유지 및 초기화
- 모델 즉시 변경 (`/model`)
- 대화 세션 저장/불러오기 (`/save`, `/load`)

---

## 1. 사전 준비

다음이 설치되어 있어야 합니다.

- Python 3.10 이상
- [Ollama](https://ollama.com/)
- 사용할 모델(최소 1개)

예시로 기본 모델을 미리 받아둡니다.

```bash
ollama pull llama3.1:8b
```

필요하면 Ollama 서버를 실행합니다.

```bash
ollama serve
```

---

## 2. 실행 방법 (Quick Start)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python local_claude.py
```

실행하면 아래처럼 프롬프트가 나타납니다.

- `🧑 You >` : 내가 입력
- `🤖 Mira >` : AI 응답

종료는 `/exit` 입력.

---

## 3. 명령어 안내

- `/help` : 명령어 도움말 보기
- `/reset` : 현재 대화 기록 초기화
- `/model <name>` : 모델 변경
  - 예: `/model qwen2.5:7b`
- `/save [path]` : 현재 대화를 파일로 저장
  - 경로 미입력 시 `chats/session-YYYYmmdd-HHMMSS.json`로 저장
- `/load <path>` : 저장한 대화 파일 불러오기
- `/exit` : 프로그램 종료

---

## 4. 환경 변수로 기본값 바꾸기

기본 설정을 바꾸고 싶다면 아래 환경 변수를 사용하세요.

- `LOCAL_AI_MODEL` (기본: `llama3.1:8b`)
- `OLLAMA_BASE_URL` (기본: `http://127.0.0.1:11434`)
- `LOCAL_AI_SYSTEM_PROMPT` (기본 시스템 프롬프트)

예시:

```bash
export LOCAL_AI_MODEL="qwen2.5:7b"
export LOCAL_AI_SYSTEM_PROMPT="항상 한국어로 답하고, 예시는 단계별로 설명해."
python local_claude.py
```

---

## 5. 트러블슈팅

### `Ollama 서버와 통신하지 못했습니다` 오류가 뜰 때

1. `ollama serve`가 실행 중인지 확인
2. `OLLAMA_BASE_URL` 값이 실제 주소와 일치하는지 확인
3. 모델이 설치되어 있는지 확인 (`ollama list`)
4. 모델 이름 오타 여부 확인 (`/model`로 변경한 경우 포함)

---

## 6. 참고

- `requirements.txt`는 **추가 서드파티 의존성이 없음을 명시**하기 위한 파일입니다.
- 실제 AI 응답은 Ollama에 설치된 모델 성능에 따라 달라집니다.
