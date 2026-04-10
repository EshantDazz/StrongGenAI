# Deep Agents with LangGraph

> Build agents that don't just answer questions — they **plan, remember, delegate, and persist** across complex, long-running tasks.

---

## What Are Deep Agents?

Standard LLM agents work well for a few tool calls. Give them a longer task — dozens or hundreds of steps — and they lose track, fill up their context window with noise, and start making poor decisions.

**Deep Agents** are a class of agents designed specifically to overcome this. Inspired by production systems like Anthropic's Claude Code, OpenAI's Deep Research, and Manus, they share four defining characteristics:

| Characteristic | Why It Matters |
|---|---|
| 🗂️ **Planning** | Keeps the agent on track over many steps |
| 💾 **File System** | Offloads context so the agent's working memory stays clean |
| 🤖 **Subagents** | Isolates focused tasks so each agent can go deep |
| 📝 **Prompting** | Steers complex behavior through detailed system prompts |

---

## The Four Pillars

### 1. 🗂️ Planning (Todo Lists)

Long agents drift. A todo list anchors them.

The agent writes a plan at the start (e.g., `todo.md`), updates it as tasks complete, and re-reads it periodically to stay grounded. This mirrors how Manus manages its trajectory and how Claude Code's plan mode works.

**Key tools:** `write_todos`, `read_todos`

```python
# The LLM writes structured todos to state
todos = [
    {"content": "Research Model Context Protocol", "status": "pending"},
    {"content": "Analyze findings and write report", "status": "pending"},
]
```

---

### 2. 💾 File System (Context Offloading)

Raw tool outputs — especially from search — are token-heavy. Dumping them all into the message history bloats the context window and degrades performance.

The file system solves this: save raw observations to files, pass only summaries back to the message list. The agent can re-fetch full content on demand.

**Key tools:** `ls`, `read_file`, `write_file`

```
Search result → save raw markdown to file (e.g., mcp_overview.md)
             → return 2-sentence summary to messages
             → agent can read_file later if needed
```

This pattern:
- Keeps the supervisor's context small and focused
- Makes summarization reversible (raw data is preserved)
- Enables long-term memory across agent steps

---

### 3. 🤖 Subagents (Context Isolation)

A single agent handling dozens of tools gets overwhelmed. Subagents solve this by giving each specialized task its own clean context window.

Each subagent has:
- Its own **system prompt** (focused on one job)
- Its own **tool set** (only what it needs)
- Its own **context window** (free of distractions)

The main (supervisor) agent only sees the subagent's **final response** — not its intermediate tool calls. This keeps the supervisor's context clean while letting subagents go arbitrarily deep.

```python
research_sub_agent = {
    "name": "research-agent",
    "description": "Delegate research tasks. Give one topic at a time.",
    "prompt": research_instructions,
    "tools": ["web_search", "think"],
}
```

> ⚠️ **Caution:** Subagents make independent decisions. Parallelizing information *gathering* is safe. Parallelizing *writing* (e.g., different agents writing different sections) risks inconsistency. Design accordingly.

---

### 4. 📝 Prompting (The Hidden Engine)

The architecture is simple — LLM + tools in a loop. What makes agents *work* is the prompt.

Production deep agents (Claude Code included) use system prompts that are **hundreds to thousands of lines long**. These prompts:
- Explain when and how to use each tool
- Define workflow sequences (e.g., "always run `ls` first")
- Set hard limits on behavior
- Guide reflection and self-correction

This is not a shortcut you can skip. Prompt quality is directly proportional to agent quality.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  Supervisor Agent                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ TodoTool │  │ FileSys  │  │  Task Tool   │   │
│  └──────────┘  └──────────┘  └──────┬───────┘   │
└──────────────────────────────────────┼───────────┘
                                       │ delegates
                          ┌────────────▼────────────┐
                          │      Subagent(s)         │
                          │  own context + tools     │
                          │  → final response only   │
                          └─────────────────────────┘
```

Built on top of LangGraph's `create_react_agent` prebuilt — a simple but powerful ReAct loop that handles tool calling, state management, and streaming out of the box.

---

## State Schema

Deep agents extend LangGraph's `AgentState` with two additional fields:

```python
class DeepAgentState(AgentState):
    todos: list[Todo]  # planned tasks + statuses
    files: dict[str, str]  # virtual file system (path → content)
```

Tools can directly update state using LangGraph's `Command` object, enabling clean separation between what the LLM produces and what gets written to state.

---

## Task Horizon Benchmark

The METR benchmark tracks how long AI agents can sustain useful work. The capability is **doubling every ~7 months**. Typical production agents now run for:

- **50+ tool calls** (Manus average)
- **Hundreds of turns** (Anthropic production agents)

Deep Agents are specifically designed to remain coherent and on-task across these long trajectories.

---

## Quick Start

```python
from langgraph.prebuilt import create_react_agent
from deepagents import file_tools, todo_tool, create_task_tool

# Define subagents
subagents = [
    {
        "name": "research-agent",
        "description": "Handles web research. One topic at a time.",
        "prompt": research_prompt,
        "tools": ["web_search"],
    }
]

# Create task delegation tool
task_tool = create_task_tool(tools=all_tools, subagents=subagents, model=model)

# Assemble the supervisor
agent = create_react_agent(
    model=model,
    tools=[*file_tools, todo_tool, task_tool],
    prompt=supervisor_prompt,
    state_schema=DeepAgentState,
)

# Run it
result = agent.invoke({"messages": [("user", "Research and summarize MCP")]})
```

---

## The `deepagents` Package

Don't want to implement all the tools yourself? The `deepagents` package wraps the file system tools, todo tool, and task tool as a ready-to-use abstraction built on `create_react_agent`.

Bring your own:
- **Custom tools** (search, APIs, databases)
- **Subagents** (specialized for your domain)
- **Prompts** (tailored to your use case)

The deep agent infrastructure comes pre-built.

---

## Key Takeaways

- Simple ReAct loops fail over long time horizons — not because of the loop, but because of unmanaged context
- Planning, files, and subagents are all fundamentally about **protecting and organizing the context window**
- The LLM architecture is simple; the **prompting** is where the real work is
- These patterns are directly drawn from Claude Code, Manus, and OpenAI Deep Research

---

*Based on the LangChain Academy course: Deep Agents with LangGraph*