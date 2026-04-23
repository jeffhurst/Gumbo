from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from gumbo.agent.services import IntentClassifier, Planner, Reflector
from gumbo.logging.traces import TraceLogger
from gumbo.memory.manager import LongTermMemory, ShortTermMemory
from gumbo.models.state import AgentState, ExecutionStatus, ToolCallRecord
from gumbo.tools.registry import ToolRegistry


class GumboGraph:
    def __init__(
        self,
        classifier: IntentClassifier,
        planner: Planner,
        reflector: Reflector,
        tools: ToolRegistry,
        short_memory: ShortTermMemory,
        long_memory: LongTermMemory,
        tracer: TraceLogger,
    ):
        self.classifier = classifier
        self.planner = planner
        self.reflector = reflector
        self.tools = tools
        self.short_memory = short_memory
        self.long_memory = long_memory
        self.tracer = tracer
        self.graph = self._build()

    def _build(self):
        graph = StateGraph(AgentState)
        graph.add_node("ingest", self.ingest)
        graph.add_node("intent", self.intent)
        graph.add_node("goal", self.goal)
        graph.add_node("plan", self.plan)
        graph.add_node("execute", self.execute)
        graph.add_node("reflect", self.reflect)
        graph.add_node("memory", self.memory)
        graph.add_node("finalize", self.finalize)

        graph.add_edge(START, "ingest")
        graph.add_edge("ingest", "intent")
        graph.add_edge("intent", "goal")
        graph.add_conditional_edges("goal", self.route_after_goal, {"plan": "plan", "finalize": "finalize"})
        graph.add_edge("plan", "execute")
        graph.add_edge("execute", "reflect")
        graph.add_conditional_edges("reflect", self.route_after_reflect, {"execute": "execute", "memory": "memory", "finalize": "finalize"})
        graph.add_edge("memory", "finalize")
        graph.add_edge("finalize", END)
        return graph.compile()

    async def ingest(self, state: AgentState) -> AgentState:
        state.normalized_input = state.raw_input.strip()
        self.tracer.log("ingest", {"session_id": state.session_id, "input": state.normalized_input})
        return state

    async def intent(self, state: AgentState) -> AgentState:
        state.intent = await self.classifier.classify(state.normalized_input)
        self.tracer.log("intent", state.intent.model_dump())
        return state

    async def goal(self, state: AgentState) -> AgentState:
        state.goal = await self.planner.goal(state.normalized_input)
        self.tracer.log("goal", {"goal": state.goal})
        return state

    def route_after_goal(self, state: AgentState) -> Literal["plan", "finalize"]:
        if state.intent and state.intent.needs_plan:
            return "plan"
        return "finalize"

    async def plan(self, state: AgentState) -> AgentState:
        state.plan = await self.planner.plan(state.goal)
        self.tracer.log("plan", {"count": len(state.plan)})
        return state

    async def execute(self, state: AgentState) -> AgentState:
        if state.current_step_index >= len(state.plan):
            return state
        step = state.plan[state.current_step_index]
        tool_name = step.tool_hint or "shell"
        args = {"command": f"echo Executing: {step.description}"} if tool_name == "shell" else {"query": step.description}
        output = await self.tools.run(tool_name, args)
        state.recent_tool_calls.append(ToolCallRecord(tool_name=tool_name, input=args, output=output, success=bool(output.get("ok"))))
        state.tool_outputs.append(str(output)[:1000])
        self.tracer.log("execute", {"step": step.description, "tool": tool_name, "ok": output.get("ok")})
        return state

    async def reflect(self, state: AgentState) -> AgentState:
        state.iterations += 1
        if state.current_step_index >= len(state.plan):
            return state
        result = state.recent_tool_calls[-1].output if state.recent_tool_calls else {"ok": False}
        verdict = await self.reflector.evaluate(result)
        step = state.plan[state.current_step_index]
        if verdict == "success":
            step.status = "completed"
            state.completed_steps.append(step.id)
            state.current_step_index += 1
        else:
            step.status = "failed"
            state.failed_steps.append(step.id)
            if state.iterations > state.max_iterations:
                state.status = ExecutionStatus.blocked
                state.final_response = "I am blocked after repeated failures."
                return state
            # simple replan in place
            step.description = f"Retry with safer approach: {step.description}"
        return state

    def route_after_reflect(self, state: AgentState) -> Literal["execute", "memory", "finalize"]:
        if state.status == ExecutionStatus.blocked:
            return "finalize"
        if state.current_step_index < len(state.plan):
            return "execute"
        return "memory"

    async def memory(self, state: AgentState) -> AgentState:
        snapshot = {
            "goal": state.goal,
            "completed_steps": state.completed_steps,
            "failed_steps": state.failed_steps,
            "recent_tools": [r.tool_name for r in state.recent_tool_calls[-5:]],
        }
        self.short_memory.set(state.session_id, "snapshot", snapshot)
        self.long_memory.maybe_store_from_state(state)
        self.tracer.log("memory", snapshot)
        return state

    async def finalize(self, state: AgentState) -> AgentState:
        if not state.final_response:
            if state.intent and not state.intent.needs_plan:
                state.final_response = f"{state.goal}\n\n(Direct response mode; no tool execution required.)"
            else:
                state.final_response = f"Completed goal: {state.goal}\nSteps completed: {len(state.completed_steps)}/{len(state.plan)}"
            if state.status == ExecutionStatus.running:
                state.status = ExecutionStatus.completed
        self.tracer.log("finalize", {"status": state.status.value, "response": state.final_response[:200]})
        return state

    async def run(self, state: AgentState) -> AgentState:
        result = await self.graph.ainvoke(state.model_dump())
        if isinstance(result, AgentState):
            return result
        return AgentState.model_validate(result)
