from __future__ import annotations

import re
from typing import Any

from gumbo.llm.ollama import OllamaAdapter
from gumbo.models.state import IntentResult, IntentType, PlanStep


class IntentClassifier:
    def __init__(self, llm: OllamaAdapter):
        self.llm = llm

    async def classify(self, text: str) -> IntentResult:
        lowered = text.lower()
        if any(w in lowered for w in ["search", "save", "write", "run", "inspect", "build", "create"]):
            return IntentResult(intent=IntentType.task, needs_tools=True, needs_plan=True)
        if len(text.split()) < 12:
            return IntentResult(intent=IntentType.chat, needs_tools=False, needs_plan=False)
        return IntentResult(intent=IntentType.question, needs_tools=False, needs_plan=False)


class Planner:
    def __init__(self, llm: OllamaAdapter):
        self.llm = llm

    async def goal(self, text: str) -> str:
        prompt = (
            "Rewrite the user's request into a concise execution goal.\n"
            "Keep meaning, remove fluff, and use one sentence.\n\n"
            f"User request:\n{text.strip()}\n\nGoal:"
        )
        try:
            goal = (await self.llm.generate(prompt=prompt)).strip()
            if goal:
                return goal.splitlines()[0][:200]
        except Exception:
            pass
        return text.strip().split("\n")[0][:200]

    async def plan(self, goal: str, user_input: str | None = None) -> list[PlanStep]:
        text = (user_input or goal).strip()
        lowered = text.lower()
        if any(w in lowered for w in ["save", "write", "create"]) and "file" in lowered:
            content_match = re.search(r'"([^"]+)"|\'([^\']+)\'', text)
            content = next((g for g in (content_match.group(1), content_match.group(2)) if g), "hello world") if content_match else "hello world"
            path_match = re.search(r"\b([\w./-]+\.[A-Za-z0-9]+)\b", text)
            path = path_match.group(1) if path_match else "test.txt"
            return [
                PlanStep(id="s1", description="Understand requirements and constraints"),
                PlanStep(
                    id="s2",
                    description="Write requested content to target file",
                    tool_hint="file_write",
                    tool_args={"path": path, "content": content, "mode": "overwrite"},
                ),
                PlanStep(
                    id="s3",
                    description="Verify saved file content",
                    tool_hint="file_read",
                    tool_args={"path": path},
                ),
            ]
        # Deterministic default plan scaffold. Future: replace with strict-JSON LLM planner.
        return [
            PlanStep(id="s1", description="Understand requirements and constraints"),
            PlanStep(id="s2", description="Choose and execute next best tool/action"),
            PlanStep(id="s3", description="Validate outcome and summarize deliverable"),
        ]

    async def decompose(self, step: PlanStep) -> list[str]:
        return [f"Execute: {step.description}"]


class Reflector:
    def __init__(self, llm: OllamaAdapter):
        self.llm = llm

    async def evaluate(self, tool_result: dict[str, Any]) -> str:
        if tool_result.get("ok"):
            return "success"
        return "failure"


class Responder:
    def __init__(self, llm: OllamaAdapter):
        self.llm = llm

    async def direct(self, user_input: str) -> str:
        prompt = (
            "Answer the user directly and helpfully.\n"
            "If the user asks for markdown, return markdown.\n\n"
            f"User:\n{user_input.strip()}\n\nAssistant:"
        )
        try:
            response = (await self.llm.generate(prompt=prompt)).strip()
            if response:
                return response
        except Exception:
            pass
        return f"I can help with that. Please try again.\n\nRequest: {user_input.strip()}"

    async def summarize_execution(self, goal: str, completed_steps: int, total_steps: int, tool_outputs: list[str]) -> str:
        tool_excerpt = "\n".join(tool_outputs[-3:])[:2500] if tool_outputs else "(no tool output)"
        prompt = (
            "Summarize the execution result for the user.\n"
            "State what was completed and include any important caveats.\n\n"
            f"Goal: {goal}\n"
            f"Progress: {completed_steps}/{total_steps} steps completed\n"
            f"Tool outputs:\n{tool_excerpt}\n\n"
            "Final answer:"
        )
        try:
            response = (await self.llm.generate(prompt=prompt)).strip()
            if response:
                return response
        except Exception:
            pass
        return f"Completed goal: {goal}\nSteps completed: {completed_steps}/{total_steps}"
