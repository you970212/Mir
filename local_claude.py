#!/usr/bin/env python3
"""Personal local AI chat bot (Claude-like assistant personality) powered by Ollama."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_MODEL = os.getenv("LOCAL_AI_MODEL", "llama3.1:8b")
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_SYSTEM_PROMPT = os.getenv(
    "LOCAL_AI_SYSTEM_PROMPT",
    (
        "You are Mira, a helpful private local AI assistant. "
        "Be clear, practical, and kind. Ask clarifying questions when needed. "
        "Use concise Korean by default unless the user asks for another language."
    ),
)


@dataclass
class LocalAIBot:
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    history: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.history.append({"role": "system", "content": self.system_prompt})

    @property
    def endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/api/chat"

    def reset(self) -> None:
        self.history = [{"role": "system", "content": self.system_prompt}]

    def save_history(self, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "system_prompt": self.system_prompt,
            "history": self.history,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
        }
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_history(self, source: Path) -> None:
        payload = json.loads(source.read_text(encoding="utf-8"))
        self.model = payload.get("model", self.model)
        self.system_prompt = payload.get("system_prompt", self.system_prompt)
        self.history = payload.get("history", [])
        if not self.history or self.history[0].get("role") != "system":
            self.history.insert(0, {"role": "system", "content": self.system_prompt})

    def ask(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": self.history,
            "stream": True,
            "options": {
                "temperature": 0.5,
                "num_ctx": 8192,
            },
        }

        print("\n🤖 Mira > ", end="", flush=True)
        assistant_message = ""

        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=180) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue
                    event = json.loads(line)
                    content = event.get("message", {}).get("content", "")
                    if content:
                        assistant_message += content
                        print(content, end="", flush=True)
                    if event.get("done"):
                        break
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            self.history.pop()
            raise RuntimeError(
                "Ollama 서버와 통신하지 못했습니다. 'ollama serve' 실행과 모델 설치를 확인하세요."
            ) from exc

        print()
        self.history.append({"role": "assistant", "content": assistant_message})
        return assistant_message


def print_help() -> None:
    print(
        """
명령어:
  /help                도움말 보기
  /reset               대화 기록 초기화
  /model <name>        모델 변경 (예: /model mistral:7b)
  /save [path]         대화 저장 (기본: chats/session-YYYYmmdd-HHMMSS.json)
  /load <path>         대화 불러오기
  /exit                종료
""".strip()
    )


def handle_command(bot: LocalAIBot, raw: str) -> bool:
    parts = raw.split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if command == "/help":
        print_help()
    elif command == "/reset":
        bot.reset()
        print("✅ 대화 기록을 초기화했습니다.")
    elif command == "/model":
        if not arg:
            print("⚠️ 사용법: /model <model-name>")
        else:
            bot.model = arg
            print(f"✅ 모델이 '{bot.model}'로 변경되었습니다.")
    elif command == "/save":
        if arg:
            target = Path(arg)
        else:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            target = Path("chats") / f"session-{stamp}.json"
        bot.save_history(target)
        print(f"✅ 대화를 저장했습니다: {target}")
    elif command == "/load":
        if not arg:
            print("⚠️ 사용법: /load <path>")
        else:
            source = Path(arg)
            if not source.exists():
                print(f"❌ 파일이 없습니다: {source}")
            else:
                bot.load_history(source)
                print(f"✅ 대화를 불러왔습니다: {source}")
    elif command == "/exit":
        print("👋 Mira를 종료합니다.")
        return False
    else:
        print("⚠️ 알 수 없는 명령입니다. /help 입력으로 확인하세요.")

    return True


def main() -> int:
    print("🧠 Mira - 개인 로컬 AI 시작")
    print(f"- 모델: {DEFAULT_MODEL}")
    print(f"- Ollama: {DEFAULT_BASE_URL}")
    print("- 종료: /exit | 도움말: /help\n")

    bot = LocalAIBot()

    while True:
        try:
            user_input = input("🧑 You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 종료합니다.")
            return 0

        if not user_input:
            continue

        if user_input.startswith("/"):
            if not handle_command(bot, user_input):
                return 0
            continue

        try:
            bot.ask(user_input)
        except RuntimeError as err:
            print(f"❌ {err}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
