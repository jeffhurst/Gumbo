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


@pytest.mark.asyncio
async def test_planner_file_write_intent_sets_tool_and_args():
    p = Planner(OllamaAdapter("http://localhost:11434", "fake"))
    text = 'use file_write to save "hello world" into test.txt'
    steps = await p.plan(text, text)
    assert steps[1].tool_hint == "file_write"
    assert steps[1].tool_args["path"] == "test.txt"
    assert steps[1].tool_args["content"] == "hello world"
    assert steps[2].tool_hint == "file_read"


@pytest.mark.asyncio
async def test_planner_goal_uses_llm():
    p = Planner(OllamaAdapter("http://localhost:11434", "fake"))

    async def fake_generate(prompt: str, system: str | None = None) -> str:
        return "Create a markdown list of favorite foods."

    p.llm.generate = fake_generate
    goal = await p.goal("draft me a markdown file of your favorite foods.")
    assert goal == "Create a markdown list of favorite foods."


@pytest.mark.asyncio
async def test_planner_search_queries_assigns_web_search_tool():
    p = Planner(OllamaAdapter("http://localhost:11434", "fake"))
    text = "conduct a websearch and report back the weather in new york and the current stock price of sp500"
    steps = await p.plan(text, text)
    assert steps[1].tool_hint == "web_search"
    assert steps[1].tool_args["query"] == text
