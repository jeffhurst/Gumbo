from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gumbo.models.state import AgentState


console = Console()


def render_state(state: AgentState, mode: str, model_name: str) -> None:
    plan_table = Table(title="Plan")
    plan_table.add_column("#")
    plan_table.add_column("Step")
    plan_table.add_column("Status")
    for step in state.plan:
        plan_table.add_row(step.id, step.description, step.status)

    tools_table = Table(title="Recent Tool Calls")
    tools_table.add_column("Tool")
    tools_table.add_column("Success")
    tools_table.add_column("Preview")
    for rec in state.recent_tool_calls[-5:]:
        tools_table.add_row(rec.tool_name, str(rec.success), str(rec.output)[:80])

    console.print(Panel(f"Mode: {mode}\nModel: {model_name}\nGoal: {state.goal}\nStatus: {state.status.value}", title="Gumbo Status"))
    if state.plan:
        console.print(plan_table)
    if state.recent_tool_calls:
        console.print(tools_table)
    console.print(Panel(state.final_response or "(No final response yet)", title="Final Answer"))
