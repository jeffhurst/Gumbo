import pytest

from gumbo.agent.services import IntentClassifier, Planner
from gumbo.llm.ollama import OllamaAdapter
from gumbo.models.state import IntentType


@pytest.mark.asyncio
async def test_intent_classifier_task():
    c = IntentClassifier(OllamaAdapter("http://localhost:11434", "fake"))
    r = await c.classify("search the web for langgraph and save notes")
    assert r.intent == IntentType.task
    assert r.needs_tools is True
    assert r.needs_plan is True


@pytest.mark.asyncio
async def test_planner_structure():
    p = Planner(OllamaAdapter("http://localhost:11434", "fake"))
    steps = await p.plan("Inspect repository and summarize")
    assert len(steps) >= 3
    assert all(step.id for step in steps)
