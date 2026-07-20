# Guardrails in LangChain

Guardrails are checks you put around an AI agent to make sure it:
- Receives safe and appropriate inputs
- Only performs approved actions
- Returns validated and compliant outputs

---

## Approaches

### 1. Deterministic
Rule-based checks — regex, keyword blocklists, format validators. Fast and predictable. No LLM involved.

### 2. Model-Based
Use an LLM to judge whether an input or output is safe. More flexible than deterministic rules. This is the approach used at Buzzboard.

### 3. Middleware (LangChain)
Add middleware layers that intercept inputs/outputs to detect sensitive data like email addresses, credit card numbers, PII, etc.

### 4. Human in the Loop
Route borderline or high-risk decisions to a human for approval before the agent proceeds.

---

## Where to Apply Them

```
User Input
    ↓
[Input Guardrail]   ← Block bad inputs before LLM even sees them
    ↓
LLM / Agent
    ↓
[Output Guardrail]  ← Validate response before sending to user
    ↓
User
```

You can layer multiple guardrails at each stage — the more sensitive the use case, the more layers you add.
