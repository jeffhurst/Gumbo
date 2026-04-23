from __future__ import annotations

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
        return text.strip().split("\n")[0][:200]

    async def plan(self, goal: str) -> list[PlanStep]:
        # Deterministic default plan scaffold. Future: replace with strict-JSON LLM planner.
        return [
            PlanStep(id="s1", description="Understand requirements and constraints"),
            PlanStep(id="s2", description="Choose and execute next best tool/action", tool_hint="shell"),
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
