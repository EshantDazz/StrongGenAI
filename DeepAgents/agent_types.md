# Understanding AI Agents: Shallow, ReAct, and Deep Agents

---

## What is an AI Agent?

An AI Agent is a system that perceives its environment, makes decisions, and takes actions
to achieve a goal. Unlike a simple chatbot that only responds to input, an agent can
**plan**, **use tools**, and **iterate** toward a solution over multiple steps.

The key differentiator between agent types is **how much reasoning and autonomy** they
exercise before producing a result.

---

## 1. Shallow Agent

### What is it?

A **Shallow Agent** is the simplest form of an agent. It receives an input, calls an LLM
once, optionally calls one tool, and returns the output. There is **no iterative loop**,
no planning, and no self-correction.

Think of it as a **single-shot** system — Input → Think once → Act once → Done.

### Characteristics

- One-step execution with no feedback loop
- No memory of previous steps during execution
- No ability to recover from errors or refine its own output
- Fast and cheap to run
- Suitable for well-defined, deterministic tasks

### When to Use

- Answering a factual question using a single tool (e.g., search)
- Summarizing a document in one pass
- Classifying or labeling data
- Simple extraction tasks

### Limitations

- Cannot handle multi-step problems
- Fails on tasks that require self-correction
- Cannot adapt if the first action produces unexpected results

---

### Shallow Agent — Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                         SHALLOW AGENT                               ║
╚══════════════════════════════════════════════════════════════════════╝

   ┌─────────────────┐
   │   USER INPUT    │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │                 │
   │   LLM  CALL     │   ← Called exactly ONCE. No loop.
   │                 │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │   TOOL CALL     │   ← Optional. Zero or one tool called.
   │  (Search / API) │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │  FINAL OUTPUT   │   ← Returned directly to the user.
   └─────────────────┘


   FLOW:  User ──► LLM ──► Tool (optional) ──► Output
   LOOP:  None
```

> **Key insight:** The LLM is called **exactly once**. If the result is wrong
> or incomplete, the agent has no way to detect or fix it.

---

## 2. ReAct Agent  (Reasoning + Acting)

### What is it?

A **ReAct Agent** (short for **Re**asoning + **Act**ing) follows an iterative loop where
the LLM alternates between:

1. **Thinking** — reasoning about what to do next
2. **Acting** — calling a tool or taking an action
3. **Observing** — reading the result of that action
4. **Repeating** — deciding whether to keep going or stop

This pattern was introduced in the paper *"ReAct: Synergizing Reasoning and Acting in
Language Models"* and is the foundation for most modern agent frameworks (LangChain,
LangGraph, AutoGPT, etc.).

### Characteristics

- Operates in a **Think → Act → Observe** loop
- Can call multiple tools across multiple steps
- Self-corrects when a tool returns unexpected results
- Stops only when the LLM decides the task is complete
- More intelligent and adaptive than a shallow agent

### The ReAct Loop — Step by Step

| Step        | What Happens                                                          |
|-------------|-----------------------------------------------------------------------|
| **Thought** | LLM reasons: *"To answer this, I need to search the web first."*     |
| **Action**  | LLM calls a tool: `search("current weather in Paris")`               |
| **Observe** | Tool returns: *"It is 18°C and cloudy in Paris."*                     |
| **Thought** | LLM reasons: *"I now have enough information to answer."*            |
| **Answer**  | Agent produces the final response.                                    |

### When to Use

- Tasks requiring multiple tool calls in sequence
- Tasks where the agent needs to verify or refine its answer
- Question answering over external data sources
- Code generation with self-debugging capability

### Limitations

- Can get stuck in infinite reasoning loops
- Each step adds latency — more loops means slower response
- The reasoning chain grows long, consuming context window
- Not ideal for tasks requiring many parallel sub-tasks

---

### ReAct Agent — Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                          REACT AGENT                                ║
╚══════════════════════════════════════════════════════════════════════╝

   ┌─────────────────┐
   │   USER INPUT    │
   └────────┬────────┘
            │
            ▼
 ╔══════════════════════════════════════════════════════╗
 ║                   AGENT  LOOP                        ║
 ║                                                      ║
 ║    ┌──────────────────────────────────────────┐      ║
 ║    │              THINK                       │      ║
 ║    │   LLM reasons: "What do I do next?"      │      ║
 ║    └───────────────────┬──────────────────────┘      ║
 ║                        │                             ║
 ║                        ▼                             ║
 ║    ┌──────────────────────────────────────────┐      ║
 ║    │               ACT                        │      ║
 ║    │   Call a tool, API, or code executor     │      ║
 ║    └───────────────────┬──────────────────────┘      ║
 ║                        │                             ║
 ║                        ▼                             ║
 ║    ┌──────────────────────────────────────────┐      ║
 ║    │             OBSERVE                      │      ║
 ║    │   Read the result returned by the tool   │      ║
 ║    └───────────────────┬──────────────────────┘      ║
 ║                        │                             ║
 ║                        ▼                             ║
 ║              ┌─────────────────┐                     ║
 ║              │  Task Complete? │                     ║
 ║              └────────┬────────┘                     ║
 ║                       │                              ║
 ║          ┌────────────┴────────────┐                 ║
 ║          │ NO                      │ YES             ║
 ║          ▼                         │                 ║
 ║    (loop back to THINK)            │                 ║
 ║                                    │                 ║
 ╚════════════════════════════════════╪════════════════╝
                                      │
                                      ▼
                           ┌─────────────────┐
                           │  FINAL OUTPUT   │
                           └─────────────────┘


   FLOW:  User ──► [ Think ──► Act ──► Observe ] × N ──► Output
   LOOP:  Continues until LLM decides task is done
```

> **Key insight:** The loop runs **as many times as needed**. Each iteration can
> use a different tool. The agent is aware of all prior steps within the session.

---

## 3. Deep Agent

### What is it?

A **Deep Agent** is a sophisticated, multi-layered system built for **complex,
long-horizon tasks** that a single ReAct agent cannot handle. It involves:

- An **Orchestrator** — the planner that breaks the goal into sub-tasks
- Multiple **Sub-agents** — each a specialist running its own ReAct loop
- **Long-term memory** — knowledge that persists across sessions
- **Parallel execution** — multiple agents working at the same time
- **Dynamic re-planning** — the plan evolves as new information arrives
- **Evaluator / Critic** — reviews quality before returning the final answer

Think of it as a **team of agents** managed by a supervisor, rather than a single
agent trying to do everything alone.

### Characteristics

- Multi-agent architecture with clear roles and hierarchy
- Hierarchical structure: planner → specialist executors
- Long-term memory persists context across sessions
- Parallel sub-task execution for efficiency
- Dynamic re-planning when unexpected results occur
- Can spawn new sub-agents on demand (agentic spawning)
- Self-evaluates and critiques its own output before responding

### Key Components

| Component            | Role                                                              |
|----------------------|-------------------------------------------------------------------|
| **Orchestrator**     | Breaks the goal, assigns sub-tasks, monitors progress            |
| **Sub-agents**       | Each handles a specialized task (search, code, writing, etc.)    |
| **Memory Store**     | Retains context, user preferences, and results from prior runs   |
| **Tool Layer**       | External tools, APIs, databases, code executors                  |
| **Evaluator/Critic** | Reviews outputs and triggers re-runs if quality is insufficient  |

### When to Use

- Research tasks spanning many sources and many steps
- End-to-end software engineering (plan → code → test → debug)
- Complex data analysis pipelines
- Any task that would naturally require a team of human specialists

### Limitations

- High latency — many agents means more round-trips
- High cost — many more LLM calls per task
- Harder to debug — failures can occur deep in the agent tree
- Requires careful orchestration to avoid redundant or conflicting work

---

### Deep Agent — Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                          DEEP AGENT                                 ║
╚══════════════════════════════════════════════════════════════════════╝

            ┌────────────────────────────┐
            │        USER INPUT          │
            │     (Complex Goal)         │
            └──────────────┬─────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │        ORCHESTRATOR          │
            │  Breaks goal into sub-tasks  │
            │  and assigns to specialists  │
            └──────┬───────────┬───────────┘
                   │           │           │
         ┌─────────┘           │           └─────────┐
         │                     │                     │
         ▼                     ▼                     ▼
 ┌───────────────┐    ┌────────────────┐    ┌───────────────┐
 │  SUB-AGENT A  │    │  SUB-AGENT B   │    │  SUB-AGENT C  │
 │  (Research)   │    │    (Code)      │    │   (Writing)   │
 │               │    │                │    │               │
 │ Think→Act     │    │  Think→Act     │    │  Think→Act    │
 │ Think→Act     │    │  Think→Act     │    │  Think→Act    │
 │    ...        │    │     ...        │    │     ...       │
 └──────┬────────┘    └───────┬────────┘    └──────┬────────┘
        │  Web/Search         │  Code Exec          │  DB/Docs
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
            ┌──────────────────────────────┐
            │         ORCHESTRATOR         │
            │   Merges all sub-agent       │
            │   results into one output    │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │      EVALUATOR / CRITIC      │
            │  Reviews quality & checks    │
            │  for errors or gaps          │
            └────────┬─────────────────────┘
                     │
         ┌───────────┴──────────────┐
         │ NOT GOOD ENOUGH          │ APPROVED
         ▼                          │
  (Re-plan and re-run               │
   back to Orchestrator)            ▼
                       ┌────────────────────────┐
                       │      MEMORY STORE      │
                       │  Saves learnings for   │
                       │  future sessions       │
                       └────────────┬───────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │   FINAL OUTPUT     │
                         └────────────────────┘


   FLOW:  User ──► Orchestrator ──► [ Sub-agents in parallel ]
                ──► Merge ──► Evaluate ──► Memory ──► Output
   LOOP:  Each sub-agent has its own ReAct loop internally
          Orchestrator re-plans if evaluation fails
```

> **Key insight:** Sub-agents run **in parallel**, each with their own Think-Act-Observe
> loop. The Evaluator ensures quality. Memory means future runs get smarter over time.

---

## How the Three Types Relate

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    EVOLUTION OF AGENT COMPLEXITY                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

  SIMPLE ◄────────────────────────────────────────────────────────► COMPLEX

  ┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
  │  SHALLOW AGENT   │        │   REACT AGENT    │        │   DEEP AGENT     │
  │                  │        │                  │        │                  │
  │  • One LLM call  │──────► │  • Think-Act     │──────► │  • Orchestrator  │
  │  • No loop       │  add   │    loop          │  add   │  • Many agents   │
  │  • No memory     │  iter- │  • Multi-tool    │  paral-│  • Parallel exec │
  │  • No self-check │  ation │  • Self-corrects │  lelism│  • Long memory   │
  │                  │        │  • Short memory  │  +eval │  • Self-evaluates│
  └──────────────────┘        └──────────────────┘        └──────────────────┘
       Fast & cheap                 Balanced                 Powerful & slow
```

---

## Side-by-Side Comparison

```
╔═══════════════════╦══════════════════╦══════════════════╦══════════════════╗
║    PROPERTY       ║  SHALLOW AGENT   ║   REACT AGENT    ║   DEEP AGENT     ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Reasoning         ║ None / minimal   ║ Step-by-step     ║ Hierarchical     ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Execution Loop    ║ No loop          ║ Think-Act loop   ║ Multi-agent      ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Tool Use          ║ Zero or one      ║ Many, in series  ║ Many, in parallel║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Memory            ║ None             ║ Short-term only  ║ Long-term        ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Self-Correction   ║ No               ║ Yes (limited)    ║ Yes (evaluator)  ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Task Complexity   ║ Low              ║ Medium           ║ High             ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Speed             ║ Fast             ║ Medium           ║ Slow             ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Cost              ║ Low              ║ Medium           ║ High             ║
╠═══════════════════╬══════════════════╬══════════════════╬══════════════════╣
║ Best For          ║ Simple lookups   ║ Multi-step Q&A   ║ Complex goals    ║
╚═══════════════════╩══════════════════╩══════════════════╩══════════════════╝
```

---

## Summary

- **Shallow Agent** — Use when the task is simple and predictable. Fast, cheap, single shot.
- **ReAct Agent** — Use when the task requires multiple steps, tool use, and self-correction.
  The workhorse of modern AI agent systems.
- **Deep Agent** — Use when the task is complex enough to require a team: parallel execution,
  long-term memory, hierarchical planning, and evaluation.

> The right agent type depends entirely on the **complexity of the task**, the **budget
> for computation**, and the **tolerance for latency**.
