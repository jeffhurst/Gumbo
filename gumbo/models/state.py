from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    chat = "chat"
    question = "question"
    task = "task"


class ExecutionStatus(str, Enum):
    running = "running"
    completed = "completed"
    blocked = "blocked"
    error = "error"


class IntentResult(BaseModel):
    intent: IntentType
    needs_tools: bool = False
    needs_plan: bool = False
    needs_clarification: bool = False
    clarification_question: str | None = None


class PlanStep(BaseModel):
    id: str
    description: str
    status: str = "pending"
    tool_hint: str | None = None


class ToolCallRecord(BaseModel):
    tool_name: str
    input: dict[str, Any]
    output: dict[str, Any]
    success: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentState(BaseModel):
    session_id: str
    user_id: str
    raw_input: str

    normalized_input: str = ""
    intent: IntentResult | None = None
    goal: str = ""

    plan: list[PlanStep] = Field(default_factory=list)
    current_step_index: int = 0
    completed_steps: list[str] = Field(default_factory=list)
    failed_steps: list[str] = Field(default_factory=list)

    recent_tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    tool_outputs: list[str] = Field(default_factory=list)

    short_term_summary: str = ""
    final_response: str = ""
    status: ExecutionStatus = ExecutionStatus.running
    iterations: int = 0
    max_iterations: int = 12


class MemoryRecord(BaseModel):
    user_id: str
    kind: str
    content: str
    score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
