# Advanced Personal Assistant AI Agent — LangGraph Mermaid Flowchart

This chart models a realistic LangGraph-style personal assistant agent with:

- a typed shared state object
- a supervisor/router
- conditional edges
- short-term and long-term memory retrieval
- explicit memory-write review
- tool routing
- human approval gates
- error recovery and replanning
- durable checkpointing

The point is not that every node must be a separate LLM call. In a real implementation, some boxes would be plain Python functions, some would be LLM-powered nodes, and some would be LangGraph prebuilt nodes such as `ToolNode`.

```mermaid
flowchart TD
    %% ============================================================
    %% ADVANCED PERSONAL ASSISTANT AI AGENT
    %% Realistic LangGraph-style architecture
    %% ============================================================

    START((Start))
    END((End))

    %% ============================================================
    %% USER AND SESSION LAYER
    %% ============================================================

    subgraph USER_SESSION["1. User & Session Layer"]
        direction TB

        USER_INPUT["User Input<br/>text, voice, image, file, event"]
        MULTIMODAL_PARSE["Normalize Input<br/>transcribe, OCR, file parse, metadata extract"]
        LOAD_THREAD["Load Conversation Thread"]
        LOAD_CHECKPOINT["Load Graph Checkpoint"]
        INIT_STATE["Initialize / Hydrate AgentState"]

        USER_INPUT --> MULTIMODAL_PARSE
        MULTIMODAL_PARSE --> INIT_STATE
        LOAD_THREAD --> INIT_STATE
        LOAD_CHECKPOINT --> INIT_STATE
    end

    START --> USER_INPUT

    %% ============================================================
    %% SHARED STATE
    %% ============================================================

    subgraph STATE["2. Shared LangGraph State"]
        direction TB

        AGENT_STATE[("AgentState<br/><br/>messages<br/>user_id<br/>session_id<br/>active_goal<br/>task_queue<br/>plan<br/>current_step<br/>retrieved_memory<br/>tool_results<br/>approvals<br/>memory_candidates<br/>citations<br/>errors<br/>final_response")]
        CHECKPOINTER[("Durable Checkpointer<br/>SQLite / Postgres / Redis")]
        EVENT_LOG[("Event Log<br/>audit trail, tool calls, decisions")]
        SESSION_CACHE[("Session Cache<br/>working memory, temporary context")]

        INIT_STATE --> AGENT_STATE
        AGENT_STATE <--> CHECKPOINTER
        AGENT_STATE --> EVENT_LOG
        AGENT_STATE <--> SESSION_CACHE
    end

    %% ============================================================
    %% ORCHESTRATION / SUPERVISOR
    %% ============================================================

    subgraph SUPERVISOR_LAYER["3. Orchestration / Supervisor"]
        direction TB

        SUPERVISOR["Supervisor / Router<br/>central graph controller"]
        SAFETY_CHECK["Safety / Policy Check<br/>allowed? constrained? risky?"]
        INTENT_CLASSIFIER["Intent Classifier<br/>chat, task, search, schedule, code, memory, file, tool"]
        URGENCY_CHECK["Urgency / Priority Check<br/>normal, time-sensitive, emergency-like"]
        CONTEXT_GAP_CHECK{"Need Clarification?"}
        DIRECT_RESPONSE_CHECK{"Can Respond Directly?"}
        GOAL_EXTRACTOR["Goal Extractor<br/>convert request into explicit objective"]
        TASK_QUEUE_UPDATE["Create / Update Task Queue"]
        REFUSE_SAFE["Safe Refusal / Safer Alternative"]
        ASK_CLARIFY["Ask Clarifying Question"]
        DRAFT_DIRECT["Draft Direct Response"]

        AGENT_STATE --> SUPERVISOR

        SUPERVISOR --> SAFETY_CHECK
        SUPERVISOR --> INTENT_CLASSIFIER
        SUPERVISOR --> URGENCY_CHECK

        SAFETY_CHECK -->|violation| REFUSE_SAFE
        SAFETY_CHECK -->|ok| CONTEXT_GAP_CHECK

        INTENT_CLASSIFIER --> CONTEXT_GAP_CHECK
        URGENCY_CHECK --> CONTEXT_GAP_CHECK

        CONTEXT_GAP_CHECK -->|yes| ASK_CLARIFY
        ASK_CLARIFY --> FINAL_DELIVERY

        CONTEXT_GAP_CHECK -->|no| DIRECT_RESPONSE_CHECK
        DIRECT_RESPONSE_CHECK -->|yes| DRAFT_DIRECT
        DIRECT_RESPONSE_CHECK -->|no| GOAL_EXTRACTOR

        GOAL_EXTRACTOR --> TASK_QUEUE_UPDATE
        TASK_QUEUE_UPDATE --> AGENT_STATE
    end

    REFUSE_SAFE --> FINAL_DELIVERY
    DRAFT_DIRECT --> RESPONSE_COMPOSER

    %% ============================================================
    %% MEMORY RETRIEVAL
    %% ============================================================

    subgraph MEMORY_READ["4. Memory Retrieval Layer"]
        direction TB

        MEMORY_QUERY_BUILDER["Build Memory Query<br/>goal + user + current context"]
        MEMORY_GATEWAY["Memory Retrieval Gateway"]
        WORKING_MEMORY[("Working Memory<br/>current turn/session")]
        PROFILE_MEMORY[("User Profile & Preferences<br/>stable facts, style, constraints")]
        EPISODIC_MEMORY[("Episodic Memory<br/>past events and interactions")]
        SEMANTIC_MEMORY[("Semantic Memory<br/>facts, concepts, summaries")]
        PROCEDURAL_MEMORY[("Procedural Memory<br/>workflows, routines, how-tos")]
        PROJECT_MEMORY[("Projects / Goals Memory<br/>open loops and active projects")]
        VECTOR_SEARCH["Vector Search / Hybrid Search<br/>embeddings + keyword + filters"]
        MEMORY_RERANK["Memory Rerank & Relevance Filter"]
        MEMORY_CONTEXT_PACK["Pack Retrieved Memory<br/>bounded, cited, task-relevant"]

        SUPERVISOR --> MEMORY_QUERY_BUILDER
        PLANNER --> MEMORY_QUERY_BUILDER
        EXECUTOR --> MEMORY_QUERY_BUILDER
        REFLECTOR --> MEMORY_QUERY_BUILDER

        MEMORY_QUERY_BUILDER --> MEMORY_GATEWAY

        MEMORY_GATEWAY --> WORKING_MEMORY
        MEMORY_GATEWAY --> PROFILE_MEMORY
        MEMORY_GATEWAY --> EPISODIC_MEMORY
        MEMORY_GATEWAY --> SEMANTIC_MEMORY
        MEMORY_GATEWAY --> PROCEDURAL_MEMORY
        MEMORY_GATEWAY --> PROJECT_MEMORY

        PROFILE_MEMORY --> VECTOR_SEARCH
        EPISODIC_MEMORY --> VECTOR_SEARCH
        SEMANTIC_MEMORY --> VECTOR_SEARCH
        PROCEDURAL_MEMORY --> VECTOR_SEARCH
        PROJECT_MEMORY --> VECTOR_SEARCH

        VECTOR_SEARCH --> MEMORY_RERANK
        MEMORY_RERANK --> MEMORY_CONTEXT_PACK
        MEMORY_CONTEXT_PACK --> AGENT_STATE
    end

    TASK_QUEUE_UPDATE --> MEMORY_QUERY_BUILDER

    %% ============================================================
    %% PLANNING
    %% ============================================================

    subgraph PLANNING["5. Planning & Reasoning Layer"]
        direction TB

        PLANNER["Planner<br/>LLM or deterministic planner"]
        GOAL_CHECK["Validate Goal<br/>specific, achievable, bounded"]
        PLAN_BUILDER["Build Plan<br/>ordered steps"]
        STEP_DECOMPOSER["Decompose Into Atomic Steps"]
        DEPENDENCY_ANALYSIS["Dependency Analysis<br/>what must happen first?"]
        TOOL_NEED_ESTIMATE["Estimate Tool Needs"]
        RISK_COST_ESTIMATE["Estimate Risk / Cost / Time"]
        STRATEGY_SELECT["Select Strategy<br/>fast path, careful path, research path"]
        PLAN_REVIEW{"Plan Good Enough?"}
        EXECUTION_PLAN["Execution Plan<br/>ready task queue"]

        AGENT_STATE --> PLANNER
        MEMORY_CONTEXT_PACK --> PLANNER

        PLANNER --> GOAL_CHECK
        GOAL_CHECK --> PLAN_BUILDER
        PLAN_BUILDER --> STEP_DECOMPOSER

        STEP_DECOMPOSER --> DEPENDENCY_ANALYSIS
        STEP_DECOMPOSER --> TOOL_NEED_ESTIMATE
        STEP_DECOMPOSER --> RISK_COST_ESTIMATE

        DEPENDENCY_ANALYSIS --> STRATEGY_SELECT
        TOOL_NEED_ESTIMATE --> STRATEGY_SELECT
        RISK_COST_ESTIMATE --> STRATEGY_SELECT

        STRATEGY_SELECT --> PLAN_REVIEW
        PLAN_REVIEW -->|no| PLAN_BUILDER
        PLAN_REVIEW -->|yes| EXECUTION_PLAN

        EXECUTION_PLAN --> AGENT_STATE
    end

    TASK_QUEUE_UPDATE --> PLANNER

    %% ============================================================
    %% HUMAN APPROVAL
    %% ============================================================

    subgraph APPROVAL["6. Approval & Consent Gates"]
        direction TB

        APPROVAL_CHECK{"Needs Human Approval?"}
        APPROVAL_REASON["Explain Proposed Action<br/>risk, side effects, cost"]
        WAIT_APPROVAL["Wait For User Approval"]
        APPROVED_CHECK{"Approved?"}
        CANCEL_OR_MODIFY["Cancel / Modify Plan"]

        APPROVAL_CHECK -->|yes| APPROVAL_REASON
        APPROVAL_REASON --> WAIT_APPROVAL
        WAIT_APPROVAL --> APPROVED_CHECK
        APPROVED_CHECK -->|yes| EXECUTOR
        APPROVED_CHECK -->|no| CANCEL_OR_MODIFY
        CANCEL_OR_MODIFY --> RESPONSE_COMPOSER

        APPROVAL_CHECK -->|no| EXECUTOR
    end

    EXECUTION_PLAN --> APPROVAL_CHECK

    %% ============================================================
    %% EXECUTION ENGINE
    %% ============================================================

    subgraph EXECUTION["7. Execution Engine"]
        direction TB

        EXECUTOR["Executor<br/>step-by-step loop"]
        SELECT_STEP["Select Next Step"]
        STEP_CONTEXT["Prepare Step Context<br/>state + memory + plan + constraints"]
        NEED_TOOL{"Need Tool?"}
        INTERNAL_REASONING["Internal Reasoning<br/>no external side effects"]
        TOOL_ROUTER["Tool Router"]
        ACTION_RESULT["Action Result"]
        UPDATE_STATE["Update AgentState"]
        STEP_COMPLETE{"Step Complete?"}
        GOAL_COMPLETE{"Goal Complete?"}
        BLOCKED_ERROR{"Blocked / Error?"}

        EXECUTOR --> SELECT_STEP
        SELECT_STEP --> STEP_CONTEXT
        STEP_CONTEXT --> NEED_TOOL

        NEED_TOOL -->|no| INTERNAL_REASONING
        INTERNAL_REASONING --> ACTION_RESULT

        NEED_TOOL -->|yes| TOOL_ROUTER

        ACTION_RESULT --> UPDATE_STATE
        UPDATE_STATE --> STEP_COMPLETE

        STEP_COMPLETE -->|no| BLOCKED_ERROR
        STEP_COMPLETE -->|yes| GOAL_COMPLETE

        GOAL_COMPLETE -->|no| SELECT_STEP
        GOAL_COMPLETE -->|yes| REFLECTOR

        BLOCKED_ERROR -->|no, continue| SELECT_STEP
        BLOCKED_ERROR -->|yes| RECOVERY_MANAGER

        UPDATE_STATE --> AGENT_STATE
        UPDATE_STATE --> MEMORY_WRITE_CANDIDATE
    end

    APPROVAL_CHECK --> EXECUTOR

    %% ============================================================
    %% TOOLS
    %% ============================================================

    subgraph TOOLS["8. Tooling Layer"]
        direction TB

        TOOL_POLICY["Tool Policy Check<br/>allowed tool? safe arguments?"]
        TOOL_EXECUTOR["Execute ToolNode<br/>standardized tool interface"]

        WEB_SEARCH["Web Search"]
        BROWSER["Browser / Page Reader"]
        CALENDAR["Calendar"]
        EMAIL["Email"]
        TASKS["Tasks / Reminders"]
        NOTES["Notes / Documents"]
        FILE_RW["File Read / Write"]
        SHELL_CODE["Shell / Code Execution"]
        DATABASE_API["Database / External APIs"]
        MAPS_TRAVEL["Maps / Travel"]
        MESSAGING["Messaging"]
        KNOWLEDGE_BASE["Knowledge Base"]
        CALCULATOR["Calculator"]
        VISION["Image / OCR / Vision"]

        TOOL_ROUTER --> TOOL_POLICY
        TOOL_POLICY --> TOOL_EXECUTOR

        TOOL_EXECUTOR --> WEB_SEARCH
        TOOL_EXECUTOR --> BROWSER
        TOOL_EXECUTOR --> CALENDAR
        TOOL_EXECUTOR --> EMAIL
        TOOL_EXECUTOR --> TASKS
        TOOL_EXECUTOR --> NOTES
        TOOL_EXECUTOR --> FILE_RW
        TOOL_EXECUTOR --> SHELL_CODE
        TOOL_EXECUTOR --> DATABASE_API
        TOOL_EXECUTOR --> MAPS_TRAVEL
        TOOL_EXECUTOR --> MESSAGING
        TOOL_EXECUTOR --> KNOWLEDGE_BASE
        TOOL_EXECUTOR --> CALCULATOR
        TOOL_EXECUTOR --> VISION

        WEB_SEARCH --> TOOL_RESULT["Tool Result<br/>structured output + provenance"]
        BROWSER --> TOOL_RESULT
        CALENDAR --> TOOL_RESULT
        EMAIL --> TOOL_RESULT
        TASKS --> TOOL_RESULT
        NOTES --> TOOL_RESULT
        FILE_RW --> TOOL_RESULT
        SHELL_CODE --> TOOL_RESULT
        DATABASE_API --> TOOL_RESULT
        MAPS_TRAVEL --> TOOL_RESULT
        MESSAGING --> TOOL_RESULT
        KNOWLEDGE_BASE --> TOOL_RESULT
        CALCULATOR --> TOOL_RESULT
        VISION --> TOOL_RESULT

        TOOL_RESULT --> ACTION_RESULT
    end

    %% ============================================================
    %% MEMORY WRITE
    %% ============================================================

    subgraph MEMORY_WRITE["9. Memory Write / Consolidation Layer"]
        direction TB

        MEMORY_WRITE_CANDIDATE["Memory Write Candidate<br/>new preference, durable fact, project update, lesson"]
        MEMORY_SAFETY["Memory Safety Filter<br/>sensitive? allowed? user-requested?"]
        MEMORY_DEDUP["Deduplicate / Merge<br/>avoid repeated memories"]
        MEMORY_SCORE["Score Memory<br/>importance, stability, usefulness"]
        STORE_MEMORY{"Store?"}
        WRITE_SHORT_TERM["Write Short-Term Memory"]
        WRITE_LONG_TERM["Write Long-Term Memory"]
        UPDATE_PROFILE["Update User Profile"]
        UPDATE_PROJECTS["Update Project / Goal State"]
        FORGET_PRUNE["Forget / Prune / Ignore"]
        MEMORY_SUMMARY["Periodic Memory Consolidation<br/>summarize old episodes"]

        MEMORY_WRITE_CANDIDATE --> MEMORY_SAFETY
        MEMORY_SAFETY --> MEMORY_DEDUP
        MEMORY_DEDUP --> MEMORY_SCORE
        MEMORY_SCORE --> STORE_MEMORY

        STORE_MEMORY -->|no| FORGET_PRUNE
        STORE_MEMORY -->|yes, temporary| WRITE_SHORT_TERM
        STORE_MEMORY -->|yes, durable| WRITE_LONG_TERM
        STORE_MEMORY -->|profile fact| UPDATE_PROFILE
        STORE_MEMORY -->|project update| UPDATE_PROJECTS

        WRITE_SHORT_TERM --> SESSION_CACHE
        WRITE_LONG_TERM --> EPISODIC_MEMORY
        UPDATE_PROFILE --> PROFILE_MEMORY
        UPDATE_PROJECTS --> PROJECT_MEMORY

        EPISODIC_MEMORY --> MEMORY_SUMMARY
        MEMORY_SUMMARY --> SEMANTIC_MEMORY
    end

    %% ============================================================
    %% REFLECTION / VALIDATION / RECOVERY
    %% ============================================================

    subgraph REFLECTION_RECOVERY["10. Reflection, Validation & Recovery"]
        direction TB

        REFLECTOR["Critic / Self-Review"]
        CHECK_GOAL["Check Against Goal"]
        VERIFY_FACTS["Verify Facts / Constraints"]
        VERIFY_TOOLS["Verify Tool Results<br/>schema, errors, stale data"]
        CONFIDENCE_SCORE["Confidence Score"]
        CONFIDENCE_DECISION{"Confidence Level?"}

        RECOVERY_MANAGER["Recovery Manager"]
        RETRY_STEP["Retry Step"]
        FALLBACK_STRATEGY["Fallback Strategy"]
        REPLAN["Replan"]
        ESCALATE_USER["Escalate / Ask User"]

        REFLECTOR --> CHECK_GOAL
        REFLECTOR --> VERIFY_FACTS
        REFLECTOR --> VERIFY_TOOLS

        CHECK_GOAL --> CONFIDENCE_SCORE
        VERIFY_FACTS --> CONFIDENCE_SCORE
        VERIFY_TOOLS --> CONFIDENCE_SCORE

        CONFIDENCE_SCORE --> CONFIDENCE_DECISION

        CONFIDENCE_DECISION -->|high| RESPONSE_COMPOSER
        CONFIDENCE_DECISION -->|medium| RETRY_STEP
        CONFIDENCE_DECISION -->|low| ESCALATE_USER

        BLOCKED_ERROR -->|error| RECOVERY_MANAGER
        RECOVERY_MANAGER --> RETRY_STEP
        RECOVERY_MANAGER --> FALLBACK_STRATEGY
        RECOVERY_MANAGER --> REPLAN
        RECOVERY_MANAGER --> ESCALATE_USER

        RETRY_STEP --> SELECT_STEP
        FALLBACK_STRATEGY --> SELECT_STEP
        REPLAN --> PLANNER
        ESCALATE_USER --> ASK_CLARIFY

        REFLECTOR --> MEMORY_WRITE_CANDIDATE
    end

    %% ============================================================
    %% RESPONSE LAYER
    %% ============================================================

    subgraph RESPONSE["11. Response Layer"]
        direction TB

        RESPONSE_COMPOSER["Response Composer"]
        SUMMARIZE_ACTIONS["Summarize Actions Taken"]
        INCLUDE_EVIDENCE["Include Evidence / Citations<br/>when required"]
        PRESENT_OPTIONS["Present Options / Next Steps"]
        FINAL_DRAFT["Final Draft"]
        FINAL_REVIEW{"Final Answer Safe & Useful?"}
        FINAL_DELIVERY["Deliver To User"]

        RESPONSE_COMPOSER --> SUMMARIZE_ACTIONS
        SUMMARIZE_ACTIONS --> INCLUDE_EVIDENCE
        INCLUDE_EVIDENCE --> PRESENT_OPTIONS
        PRESENT_OPTIONS --> FINAL_DRAFT
        FINAL_DRAFT --> FINAL_REVIEW
        FINAL_REVIEW -->|no| RESPONSE_COMPOSER
        FINAL_REVIEW -->|yes| FINAL_DELIVERY

        FINAL_DELIVERY --> SAVE_TURN["Save Conversation Turn"]
        SAVE_TURN --> CHECKPOINTER
        SAVE_TURN --> EVENT_LOG
        SAVE_TURN --> END
    end

    %% ============================================================
    %% BACKGROUND / EVENT-DRIVEN FLOWS
    %% ============================================================

    subgraph BACKGROUND["12. Background & Scheduled Flows"]
        direction TB

        EXTERNAL_EVENT["External Event Trigger<br/>calendar event, email, webhook, reminder"]
        SCHEDULED_WAKE["Scheduled Wake-Up"]
        BACKGROUND_TASK["Background Task Runner"]
        NOTIFICATION_POLICY["Notification Policy<br/>should interrupt user?"]
        BACKGROUND_RESULT["Background Result"]

        EXTERNAL_EVENT --> BACKGROUND_TASK
        SCHEDULED_WAKE --> BACKGROUND_TASK
        BACKGROUND_TASK --> NOTIFICATION_POLICY
        NOTIFICATION_POLICY -->|silent update| MEMORY_WRITE_CANDIDATE
        NOTIFICATION_POLICY -->|notify user| BACKGROUND_RESULT
        BACKGROUND_RESULT --> SUPERVISOR
    end

    EXTERNAL_EVENT --> LOAD_CHECKPOINT
    SCHEDULED_WAKE --> LOAD_CHECKPOINT

    %% ============================================================
    %% REALISTIC LANGGRAPH CONDITIONAL EDGE SUMMARY
    %% ============================================================

    ROUTING_NOTE["Typical Conditional Edges<br/><br/>route_after_supervisor:<br/>clarify | direct | plan | refuse<br/><br/>route_after_step:<br/>continue | tool | reflect | recover<br/><br/>route_after_reflection:<br/>respond | retry | replan | ask_user<br/><br/>route_memory_write:<br/>ignore | short_term | long_term | profile | project"]

    SUPERVISOR -.-> ROUTING_NOTE
    EXECUTOR -.-> ROUTING_NOTE
    REFLECTOR -.-> ROUTING_NOTE
    MEMORY_WRITE_CANDIDATE -.-> ROUTING_NOTE

    %% ============================================================
    %% STYLES
    %% ============================================================

    classDef startEnd fill:#111827,stroke:#111827,color:#ffffff,stroke-width:2px;
    classDef user fill:#e0f2fe,stroke:#0369a1,color:#0c4a6e,stroke-width:1.5px;
    classDef state fill:#fef3c7,stroke:#b45309,color:#78350f,stroke-width:1.5px;
    classDef supervisor fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a,stroke-width:1.5px;
    classDef memory fill:#ccfbf1,stroke:#0f766e,color:#134e4a,stroke-width:1.5px;
    classDef planning fill:#ede9fe,stroke:#6d28d9,color:#3b0764,stroke-width:1.5px;
    classDef execution fill:#dcfce7,stroke:#15803d,color:#14532d,stroke-width:1.5px;
    classDef tools fill:#ffedd5,stroke:#ea580c,color:#7c2d12,stroke-width:1.5px;
    classDef approval fill:#fce7f3,stroke:#be185d,color:#831843,stroke-width:1.5px;
    classDef recovery fill:#fee2e2,stroke:#dc2626,color:#7f1d1d,stroke-width:1.5px;
    classDef response fill:#f3f4f6,stroke:#374151,color:#111827,stroke-width:1.5px;
    classDef decision fill:#ffffff,stroke:#7c3aed,color:#312e81,stroke-width:2px;
    classDef note fill:#f9fafb,stroke:#6b7280,color:#374151,stroke-dasharray: 5 5;

    class START,END startEnd;

    class USER_INPUT,MULTIMODAL_PARSE,LOAD_THREAD,LOAD_CHECKPOINT,INIT_STATE user;

    class AGENT_STATE,CHECKPOINTER,EVENT_LOG,SESSION_CACHE state;

    class SUPERVISOR,SAFETY_CHECK,INTENT_CLASSIFIER,URGENCY_CHECK,GOAL_EXTRACTOR,TASK_QUEUE_UPDATE,REFUSE_SAFE,ASK_CLARIFY,DRAFT_DIRECT supervisor;

    class MEMORY_QUERY_BUILDER,MEMORY_GATEWAY,WORKING_MEMORY,PROFILE_MEMORY,EPISODIC_MEMORY,SEMANTIC_MEMORY,PROCEDURAL_MEMORY,PROJECT_MEMORY,VECTOR_SEARCH,MEMORY_RERANK,MEMORY_CONTEXT_PACK,MEMORY_WRITE_CANDIDATE,MEMORY_SAFETY,MEMORY_DEDUP,MEMORY_SCORE,WRITE_SHORT_TERM,WRITE_LONG_TERM,UPDATE_PROFILE,UPDATE_PROJECTS,FORGET_PRUNE,MEMORY_SUMMARY memory;

    class PLANNER,GOAL_CHECK,PLAN_BUILDER,STEP_DECOMPOSER,DEPENDENCY_ANALYSIS,TOOL_NEED_ESTIMATE,RISK_COST_ESTIMATE,STRATEGY_SELECT,EXECUTION_PLAN planning;

    class EXECUTOR,SELECT_STEP,STEP_CONTEXT,INTERNAL_REASONING,TOOL_ROUTER,ACTION_RESULT,UPDATE_STATE execution;

    class TOOL_POLICY,TOOL_EXECUTOR,WEB_SEARCH,BROWSER,CALENDAR,EMAIL,TASKS,NOTES,FILE_RW,SHELL_CODE,DATABASE_API,MAPS_TRAVEL,MESSAGING,KNOWLEDGE_BASE,CALCULATOR,VISION,TOOL_RESULT tools;

    class APPROVAL_CHECK,APPROVAL_REASON,WAIT_APPROVAL,APPROVED_CHECK,CANCEL_OR_MODIFY approval;

    class REFLECTOR,CHECK_GOAL,VERIFY_FACTS,VERIFY_TOOLS,CONFIDENCE_SCORE,RECOVERY_MANAGER,RETRY_STEP,FALLBACK_STRATEGY,REPLAN,ESCALATE_USER recovery;

    class RESPONSE_COMPOSER,SUMMARIZE_ACTIONS,INCLUDE_EVIDENCE,PRESENT_OPTIONS,FINAL_DRAFT,FINAL_DELIVERY,SAVE_TURN response;

    class CONTEXT_GAP_CHECK,DIRECT_RESPONSE_CHECK,PLAN_REVIEW,NEED_TOOL,STEP_COMPLETE,GOAL_COMPLETE,BLOCKED_ERROR,STORE_MEMORY,CONFIDENCE_DECISION,FINAL_REVIEW decision;

    class ROUTING_NOTE note;
```

## Implementation Notes

### 1. Suggested `AgentState`

A realistic LangGraph implementation would usually pass one shared state object through the graph.

```python
from typing import Annotated, TypedDict, Literal
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    session_id: str

    active_goal: str | None
    task_queue: list[dict]
    plan: list[dict]
    current_step: dict | None

    retrieved_memory: list[dict]
    tool_results: list[dict]
    approvals: list[dict]
    memory_candidates: list[dict]

    citations: list[dict]
    errors: list[dict]
    final_response: str | None
```

### 2. Realistic node types

Not every node should be an LLM call.

| Node Type | Good Implementation |
|---|---|
| Safety check | deterministic rules + model classifier when needed |
| Intent classifier | small/fast LLM or rules |
| Planner | stronger LLM |
| Tool router | LLM tool calling or explicit routing |
| Tool execution | LangGraph `ToolNode` |
| Memory retrieval | vector DB + keyword search + reranker |
| Memory scoring | rules + LLM judgment for ambiguous memories |
| Reflection | LLM critic + deterministic validation |
| Checkpointer | SQLite/Postgres/Redis checkpointer |

### 3. Memory should not be automatic garbage collection

A good assistant does **not** blindly store everything. It should score memory candidates using questions like:

- Is this stable over time?
- Will this help future conversations?
- Did the user explicitly ask me to remember it?
- Is it sensitive?
- Is it already stored?
- Is it a temporary task detail or a durable preference?

### 4. Practical storage split

| Memory Type | Storage |
|---|---|
| Working memory | LangGraph state |
| Session memory | checkpointer / cache |
| Long-term user profile | database table |
| Episodic memory | vector DB + metadata |
| Semantic summaries | vector DB or document store |
| Project state | structured database rows |
| Tool/event log | append-only event table |

### 5. Core loop

The practical loop is:

```text
input
→ hydrate state
→ retrieve relevant memory
→ route intent
→ clarify or plan
→ execute next step
→ use tools if needed
→ update state
→ reflect
→ retry/replan/respond
→ write approved memory
→ checkpoint
→ respond
```

That is the pattern you want for something like Gumbo.
