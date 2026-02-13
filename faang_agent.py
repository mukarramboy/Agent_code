"""Simple FAANG-style task agent with auto mode and convenient local run options."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Mode = Literal["email", "code", "analysis"]
InputMode = Literal["email", "code", "analysis", "auto"]


@dataclass
class AgentResponse:
    mode: Mode
    context: str
    plan: str
    output: str
    risks: str
    next_steps: str

    def render(self) -> str:
        return (
            f"Mode: {self.mode}\n\n"
            f"Context\n{self.context}\n\n"
            f"Plan\n{self.plan}\n\n"
            f"Output\n{self.output}\n\n"
            f"Risks\n{self.risks}\n\n"
            f"Next steps\n{self.next_steps}\n"
        )


class FaangSeniorAgent:
    """Rule-based multi-skill assistant with FAANG-style response structure."""

    def run(self, task: str, mode: InputMode = "auto") -> AgentResponse:
        resolved_mode = self._resolve_mode(task, mode)
        if resolved_mode == "email":
            return self._handle_email(task)
        if resolved_mode == "code":
            return self._handle_code(task)
        return self._handle_analysis(task)

    def _resolve_mode(self, task: str, mode: InputMode) -> Mode:
        if mode != "auto":
            return mode

        lowered = task.lower()
        email_keywords = ("email", "письм", "ответь", "клиент", "заказчик")
        code_keywords = ("код", "функц", "class", "api", "python", "bug", "fix")

        if any(token in lowered for token in email_keywords):
            return "email"
        if any(token in lowered for token in code_keywords):
            return "code"
        return "analysis"

    def _handle_email(self, task: str) -> AgentResponse:
        return AgentResponse(
            mode="email",
            context=f"Нужно ответить на email по задаче: {task}",
            plan=(
                "1) Подтвердить получение и ownership. "
                "2) Зафиксировать ожидаемый срок ответа. "
                "3) Спросить недостающие детали для ускорения решения."
            ),
            output=(
                "Здравствуйте!\n"
                "Спасибо за обращение — запрос получен и назначен в работу нашей команде. "
                "Первичное обновление по статусу отправим до конца рабочего дня. "
                "Если есть логи/скриншоты/шаги воспроизведения, пришлите их ответом на это письмо — это ускорит решение.\n\n"
                "С уважением,\n"
                "Engineering Team"
            ),
            risks="Если не указать SLA и ответственного, коммуникация может затянуться.",
            next_steps="Подставить фактический SLA, имя ответственного и канал эскалации.",
        )

    def _handle_code(self, task: str) -> AgentResponse:
        return AgentResponse(
            mode="code",
            context=f"Запрошена инженерная реализация: {task}",
            plan=(
                "1) Уточнить интерфейс и ограничения. "
                "2) Дать рабочую реализацию + пример использования. "
                "3) Покрыть edge cases тестами."
            ),
            output=(
                "```python\n"
                "from functools import wraps\n"
                "from threading import RLock\n"
                "import time\n\n"
                "def ttl_cache(ttl_seconds: int, maxsize: int = 256):\n"
                "    if ttl_seconds <= 0:\n"
                "        raise ValueError('ttl_seconds must be > 0')\n"
                "    if maxsize <= 0:\n"
                "        raise ValueError('maxsize must be > 0')\n\n"
                "    def decorator(fn):\n"
                "        cache = {}\n"
                "        order = []\n"
                "        lock = RLock()\n\n"
                "        @wraps(fn)\n"
                "        def wrapper(*args, **kwargs):\n"
                "            key = (args, tuple(sorted(kwargs.items())))\n"
                "            now = time.time()\n"
                "            with lock:\n"
                "                if key in cache:\n"
                "                    ts, val = cache[key]\n"
                "                    if now - ts < ttl_seconds:\n"
                "                        return val\n"
                "                    del cache[key]\n"
                "                    order.remove(key)\n\n"
                "                value = fn(*args, **kwargs)\n"
                "                cache[key] = (now, value)\n"
                "                order.append(key)\n"
                "                if len(order) > maxsize:\n"
                "                    old = order.pop(0)\n"
                "                    cache.pop(old, None)\n"
                "                return value\n"
                "        return wrapper\n"
                "    return decorator\n"
                "```"
            ),
            risks="Ключ кэша не подойдет для не-хэшируемых аргументов (например, list/dict).",
            next_steps="Добавить сериализацию ключей и метрики hit/miss.",
        )

    def _handle_analysis(self, task: str) -> AgentResponse:
        project_stats = self._scan_project()
        return AgentResponse(
            mode="analysis",
            context=f"Задача: {task}. Текущее состояние проекта: {project_stats}",
            plan=(
                "1) Оценить состав кодовой базы и артефактов. "
                "2) Выделить риски в архитектуре и процессах. "
                "3) Дать поэтапный roadmap улучшений."
            ),
            output=(
                "Архитектурное заключение:\n"
                "- Разделите слой бизнес-логики, инфраструктуры и интерфейсов.\n"
                "- Добавьте единый стандарт логирования + correlation-id.\n"
                "- В CI зафиксируйте quality gates: lint, tests, security scan, dependency audit.\n"
                "- Для агентных действий введите policy layer и audit trail."
            ),
            risks="Без автотестов и guardrails агент может выполнять рискованные действия.",
            next_steps="Добавить интеграцию LLM API, memory storage и безопасные tool adapters.",
        )

    def _scan_project(self) -> str:
        tracked = [p for p in Path(".").rglob("*") if p.is_file() and ".git" not in p.parts]
        ext_counter: Counter[str] = Counter(p.suffix.lower() or "[no_ext]" for p in tracked)
        top_ext = ", ".join(f"{k}:{v}" for k, v in ext_counter.most_common(3)) or "n/a"
        return f"files={len(tracked)}, top_extensions=({top_ext})"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FAANG-style senior agent")
    parser.add_argument(
        "--mode",
        default="auto",
        choices=["email", "code", "analysis", "auto"],
        help="Execution mode (default: auto)",
    )
    parser.add_argument("--task", help="Task description")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode: ask for task in terminal",
    )
    return parser.parse_args()


def _resolve_task(args: argparse.Namespace) -> str:
    if args.task:
        return args.task
    if args.interactive:
        return input("Введите задачу для агента: ").strip()
    raise SystemExit("Ошибка: передайте --task или используйте --interactive")


def main() -> None:
    args = parse_args()
    task = _resolve_task(args)
    agent = FaangSeniorAgent()
    response = agent.run(task=task, mode=args.mode)
    print(response.render())


if __name__ == "__main__":
    main()
